from .base import (
    AsyncDataDriver, 
    UriConnMixin, 
    AsyncEndpoint,
    AsyncLoop,
    run_asyn
    )

from fairways.io.generic.net import (
    AmqpQueueTemplate,
    AmqpExchangeTemplate
)

from fairways.funcflow import FuncFlow as ff

import functools

import threading
import asyncio
import aio_pika

from typing import (
    Callable, 
    Awaitable, 
    NamedTuple, 
    List,
    Dict, 
    Type, 
    TypeVar, 
    Optional,
    Any)

from fairways.decorators import (entities, entrypoint)

import logging
log = logging.getLogger()
log.setLevel(level=logging.DEBUG)

# Error with single 
EIgnoreErrors = (

)

EReconnectOnErrors = (

)

EHaltOnErrors = (
    aio_pika.exceptions.AMQPChannelError, 
    aio_pika.exceptions.AMQPConnectionError, 
    aio_pika.exceptions.AMQPError, 
    aio_pika.exceptions.AMQPException, 
    aio_pika.exceptions.AuthenticationError, 
    *aio_pika.exceptions.CONNECTION_EXCEPTIONS, 
    aio_pika.exceptions.ChannelClosed, 
    aio_pika.exceptions.ChannelNotFoundEntity, 
    aio_pika.exceptions.ChannelPreconditionFailed, 
    aio_pika.exceptions.ConnectionClosed, 
    aio_pika.exceptions.DeliveryError, 
    aio_pika.exceptions.DuplicateConsumerTag, 
    aio_pika.exceptions.IncompatibleProtocolError, 
    aio_pika.exceptions.InvalidFrameError, 
    aio_pika.exceptions.MessageProcessError, 
    aio_pika.exceptions.MethodNotImplemented, 
    *aio_pika.exceptions.PAMQP_EXCEPTIONS, 
    aio_pika.exceptions.ProbableAuthenticationError, 
    aio_pika.exceptions.ProtocolSyntaxError, 
)

DEFAULT_QUEUE_SETTINGS = dict(
    durable = True, 
    auto_delete = False,
    exclusive = False,
    passive = True,    
)

#: Types:
MessageBody = TypeVar('MessageBody', str, bytes)
ConnectionFactory = Callable[[], Awaitable[aio_pika.connection.Connection]]
ChannelFactory = Callable[[aio_pika.connection.Connection], Awaitable[aio_pika.channel.Channel]]
AmqpQueueFactory = Callable[[aio_pika.channel.Channel], Awaitable[aio_pika.queue.Queue]]
AmqpExchangeFactory = Callable[[aio_pika.channel.Channel], Awaitable[aio_pika.exchange.Exchange]]

class AmqpQueueRecord(NamedTuple):
    channel: aio_pika.channel.Channel
    queue: aio_pika.queue.Queue
    # # Only for checking:
    # queue_settings: Dict[str, Any]

class AmqpExchangeRecord(NamedTuple):
    channel: aio_pika.channel.Channel
    exchange: aio_pika.exchange.Exchange
    # # Only for checking:
    # exchange_settings: Dict[str, Any]

class ConnectionRecord(NamedTuple):
    """ Container for connections and related channels """

    connection: Optional[aio_pika.connection.Connection]
    # channel_recs: Dict[str, Union[AmqpQueueRecord, AmqpExchangeRecord]]
    queue_channels: Dict[str, AmqpQueueRecord]
    exchange_channels: Dict[str, AmqpExchangeRecord]

    async def _close_items(reg: Dict[str, Any]):
        while reg:
            (name, channel_record) = reg.popitem()
            try:
                await channel_record.channel.close()
            except Exception as e:
                log.debug('Error closing channel: %s', name)

    async def close_exchanges(self):
        """Close exchange channels for this connection
        """
        await self._close_items(self.exchange_channels)

    async def close_queues(self):
        """Close queue channels for this connection
        """
        await self._close_items(self.queue_channels)
    
    async def close_channel(self, name: str):
        async def try_close(reg):
            channel_rec = reg.get(name)
            if channel_rec is not None:
                await channel_rec.connection.close()
                del reg[name]
        await try_close(self.queue_channels)
        await try_close(self.exchange_channels)
    
    async def get_exchange(self, *, 
            exchange_name: str,
            exchange_settings: Dict[str, Any]) -> aio_pika.exchange.Exchange:

        channel_rec = self.exchange_channels.get(exchange_name)
        if channel_rec is None:
            channel = await self.connection.channel()
            exchange = await channel.declare_exchange(
                    exchange_name, **exchange_settings)
            channel_rec = AmqpExchangeRecord(channel, exchange)
        return channel_rec.exchange

    async def get_queue(self, 
            queue_name: str, *,
            queue_settings: Dict[str, Any]) -> aio_pika.queue.Queue:

        channel_rec = self.queue_channels.get(queue_name)
        if channel_rec is None:
            channel = await self.connection.channel()
            await channel.set_qos(prefetch_count=1)
            queue = await channel.declare_queue(queue_name, **queue_settings)
            channel_rec = AmqpQueueRecord(channel, queue)
        return channel_rec.queue

    def get_names(self):
        return list(self.queue_channels.keys()) + list(self.exchange_channels.keys())

class ConnRegistry:
    """ Registry for all connections and their channels.
    Structure:
    One connection per thread
    Seperate channels for producers and consumers
    One channel per queue/exchange name
    """
    def __init__(self, amqp_url: str):
        self.connection_by_thread = {}
        self.amqp_url = amqp_url
    
    def get_current_connection_rec(self) -> Optional[ConnectionRecord]:
        """Connection for current thread
        
        :return: Current connection if any
        :rtype: Optional[ConnectionRecord]
        """
        tid = threading.get_ident()
        return self.connection_by_thread.get(tid)
    
    async def get_connection_rec(self) -> ConnectionRecord:
        """Retrieve existing connection for current thread or create new if necessary
        
        :param connection_factory: Factory function (without parameters)
        :type connection_factory: Awaitable
        :return: Connection record
        :rtype: ConnectionRecord
        """
        # Keep 1 connection per thread
        tid = threading.get_ident()
        conn_rec = self.connection_by_thread.get(tid)
        if conn_rec is None:
            # conn_obj = await connection_factory()
            conn_obj = await aio_pika.connect(self.amqp_url)
            conn_rec = ConnectionRecord(conn_obj, {}, {})
            self.connection_by_thread[tid] = conn_rec
        return conn_rec
        
    def connections_rec_list(self) -> List[ConnectionRecord]:
        """List of connections for all threads
        
        :return: List of records
        :rtype: List[ConnectionRecord]
        """
        return list(self.connection_by_thread.values())

    async def close_current_connection(self):
        tid = threading.get_ident()
        connection = self.connection_by_thread.get(tid)
        if connection is not None:
            await connection.close()
            del self.connection_by_thread[tid]

class AmqpDriver(AsyncDataDriver, UriConnMixin):
    """AMQP/RabbitMQ driver.
    Requires `aio-pika <https://aio-pika.readthedocs.io/>`_.
    
    :param env_varname: Name of enviromnent variable (or settings attribute) which holds connection string (e.g.: "mysql://user@pass@host/db")
    :type env_varname: str
    """

    #: Default connection string (for testing)
    default_conn_str = "amqp://guest:guest@localhost:5672/%2f"

    #: Do not close connection after single request
    autoclose = False


    def is_connected(self) -> bool:
        """Connection alive flag
        
        :return: True when connected
        :rtype: bool
        """
        raise NotImplementedError("Should not be called, AMQP driver uses another approach")
        # return self.engine is not None and not self.engine.is_closed

    async def _connect(self):
        # conn_str = self.conn_str
        # engine = await aio_pika.connect(conn_str)
        # self.engine = engine
        # channel = await engine.channel()
        # self.channel = channel
        raise NotImplementedError("Should not be called, AMQP driver uses another approach")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._connections_registry = ConnRegistry(self.conn_str)

    async def close(self) -> None:
        """Close connection. 
        Does nothing if already closed.
        """
        conn_rec = self._connections_registry.get_current_connection_rec()
        if conn_rec is not None:
            await conn_rec.close_queues()
            await conn_rec.close_exchanges()
        # if self.is_connected():
        #     await self.channel.close()
        #     self.channel = None
        #     await self.engine.close()
        #     self.engine = None

    def execute(self, _, *,
            body: MessageBody, 
            exchange: str,
            exchange_settings=None,
            routing_key:str=None,
            headers:Dict=None,
            content_type:str=None
            ) -> Awaitable:
        """Returns awaitable which should publish message.
        
        :param _: Ignored (only for consistency with BaseDriver signature)
        :type _: Any
        :raises Exception: Re-raise exceptions of underlying engine
        :return: Awaitable to publish message
        :rtype: Awaitable
        """

        exchange_settings = exchange_settings or AmqpExchangeTemplate.default_exchange_settings()
        routing_key = routing_key or ""
        message = body
        headers = headers or {}
        content_type = content_type or "text/plain"
        exchange_name = exchange
        if isinstance(message, str):
            body = message.encode()
        elif isinstance(message, bytes):
            body = message # Ok
        else:
            raise Exception(f"Unsupported type of message: {type(message)}")

        async def push():

            connection_rec = await self._connections_registry.get_connection_rec()
            exchange = await connection_rec.get_exchange(
                exchange_name = exchange_name, 
                exchange_settings=exchange_settings)

            try:
                log.debug("Sending AMQP message")

                await exchange.publish(
                    aio_pika.Message(
                        body=body,
                        headers=headers,
                        content_type=content_type
                    ),
                    routing_key=routing_key
                )

            except Exception as e:
                log.error("AMQP operation error: %r at %s;", e, params)
                raise
        
        return push()


    def get_records(self, _, *, 
            queue_name, 
            queue_settings=None) -> Awaitable:
        """Returns awaitable which should consume messages.
        
        :param _: Ignored (only for consistency with BaseDriver signature)
        :type _: Any
        :raises Exception: Re-raise exceptions of underlying engine
        :return: Awaitable to fetch message
        :rtype: Awaitable
        """
        queue_settings = ff.weld(queue_settings or {}, AmqpQueueTemplate.default_queue_settings())
        # queue_settings = queue_settings or AmqpQueueTemplate.default_queue_settings()

        async def pull():
            try:
                connection_rec = await self._connections_registry.get_connection_rec()
                queue = await connection_rec.get_queue(
                    queue_name=queue_name, 
                    queue_settings=queue_settings)
            except Exception as e:
                log.error("ERROR on Queue: %r", e)
                raise
            try:
                log.debug("Receiving AMQP message")

                incoming_message = await queue.get(queue_settings["timeout"], fail=False)
                if incoming_message is not None:
                    return [incoming_message]
                return []

                # async with queue.iterator() as queue_iter:
                #     async for message in queue_iter:
                #         async with message.process():
                #             return message

            except Exception as e:
                log.error("AMQP operation error: %r at %s;", e, params)
                raise
        
        return pull()

    async def _consume_asyn(self, asyn_c, **params):
        # Use receipt from: https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.run_in_executor
        queue_name = params["queue"]
        queue_settings = params.get("queue_settings", DEFAULT_QUEUE_SETTINGS)

        try:
            await self._ensure_connection()
            connection = self.engine
            channel = await connection.channel()    # type: aio_pika.Channel

            await channel.set_qos(prefetch_count=1)

            queue = await channel.declare_queue(queue_name, **queue_settings)

            log.debug("Starting AMQP consumer loop")

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        await asyn_c(message)
                        await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            log.info("Task cancelled")

        except Exception as e:
            log.error("AMQP operation error: {} at {};".format(e, queue_name))
            raise
        finally:
            if self.autoclose:
                await self.close()
        

    def consume(self, asyn_c, **params):
        # Use in consumer decorator directly???
        """Run consumer with callback. 
        This is blocking function.
        Tentative feature.
        
        :param asyn_c: Asyncronous callback
        :type asyn_c: Awaitable
        """
        run_asyn(self._consume_asyn(asyn_c, **params))

    async def input_stream(self, *, 
            queue_name, 
            queue_settings=None):
        
        """Message stream.
        Used in AsynAmqpConsumerLoop.
        
        :yield: Next message
        :rtype: aiopika.IncomingMessage
        """
        
        queue_settings = ff.weld(queue_settings or {}, AmqpQueueTemplate.default_queue_settings())

        try:
            connection_rec = await self._connections_registry.get_connection_rec()
            queue = await connection_rec.get_queue(
                queue_name=queue_name, 
                queue_settings=queue_settings)
        except Exception as e:
            log.error("QUEUE ERROR: %r", e)
            raise

        log.debug("AmqpDriver: Starting AMQP consumer loop")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    yield message
                    await asyncio.sleep(0.1)

    async def output_stream(self, *, 
            aio_queue: asyncio.Queue,
            exchange_name: str,
            exchange_settings: Dict[str, Any]=None,
            ):

        exchange_settings = exchange_settings or AmqpExchangeTemplate.default_exchange_settings()
        keep_running = True
        log.debug("AmqpDriver: Starting AMQP producer loop")
        while keep_running:
            # Outer loop for reliable connection
            
            log.debug("AmqpDriver.output_stream [entering loop]")
            try:
                connection_rec = await self._connections_registry.get_connection_rec()
                exchange = await connection_rec.get_exchange(
                    exchange_name=exchange_name, 
                    exchange_settings=exchange_settings)
            except Exception as e:
                log.error("CONN ERROR: %r", e)
                raise

            try:
                while True:
                    log.debug("Waiting for message")
                    message = await aio_queue.get()
                    log.debug("Message occurs: %s", message)
                    if not isinstance(message, dict):
                        log.error("Message should be a dict, but type is %s", type(message))
                        continue

                    body = message["body"]
                    routing_key = message.get("routing_key", "")
                    headers = message.get("headers", {})
                    content_type = message.get("content_type", "text/plain")

                    if isinstance(body, str):
                        body=body.encode()

                    await exchange.publish(
                        aio_pika.Message(
                            body=body,
                            headers=headers,
                            content_type=content_type
                        ),
                        routing_key=routing_key
                    )

                    aio_queue.task_done()

            except asyncio.CancelledError:
                log.debug("AmqpDriver.output_stream - Cancelling [exiting loop]")
                keep_running = False
                break

            except Exception as e:
                # TODO: amqp.py: Refactor recommection loop and use same approach for input_stream()!!!!!!
                log.error("EXCEPTION occurs: %s", e)
                e_cls = e.__class__
                if e_cls in EIgnoreErrors:
                    log.warning("AmqpDriver.output_stream: EIgnoreErrors condition")
                    pass
                elif e_cls in EReconnectOnErrors:
                    # TODO: close exchange channel and / or connection
                    log.warning("AmqpDriver.output_stream: EReconnectOnErrors condition")
                    pass
                else:
                    log.debug("AmqpDriver.output_stream [exiting loop]")
                    keep_running = False
                    break



class AsyncAmqpConsumerLoop(AsyncLoop):

    def __init__(self, driver_instance, decorated_task, *, queue_name, queue_settings):
        super().__init__()
        self.driver_instance = driver_instance
        self.decorated_task = decorated_task
        self.queue_name = queue_name
        self.queue_settings = queue_settings
        
    async def input_stream(self):
        async for message in self.driver_instance.input_stream(queue_name=self.queue_name, queue_settings=self.queue_settings):
            try:
                yield message
            except asyncio.CancelledError:
                break

    async def output_stream(self, message):

        loop = asyncio.get_event_loop()

        # 1. Run in the default loop's executor:
        result = await loop.run_in_executor(
            None, self.decorated_task, message)
        log.debug('Task flow result ready: %s', result)
        

class AsyncAmqpProducerLoop(AsyncLoop):

    def __init__(self, driver_instance, queue_bus, *, 
            exchange_name, 
            exchange_settings=None):
        super().__init__()
        self.driver_instance = driver_instance
        self.queue_bus = queue_bus
        self.exchange_name = exchange_name
        self.exchange_settings = exchange_settings
        
    async def input_stream(self):
        while not self.GLOBAL_STOP_EVENT.is_set():
            try:
                item = await self.queue_bus.get()
                log.debug("Message in input_stream...")
                self.queue_bus.task_done()
                # TODO: message implicit typecast - restore
                if isinstance(item, (str, bytes)):
                    item = dict(body=item)
                yield item
            except asyncio.CancelledError:
                log.info("AsyncAmqpProducerLoop.process_input cancelled")
                break

    async def process_output(self, queue:asyncio.Queue):
        await self.driver_instance.output_stream(
            # aio_queue=self.queue_bus,
            aio_queue=queue,
            exchange_name=self.exchange_name,
            exchange_settings=self.exchange_settings,
        )

    async def output_stream(self, message):
        raise NotImplementedError("Should not be called")


@entities.register_decorator
class AmqpConsumerDecorator(AsyncEndpoint, entrypoint.Listener):
    """Decorator to mark a consumer endpoint (a consumer function or a consumer chain)
    Usage:

    .. code-block:: python

        @amqp.consumer(queue="fairways")
        def run(message):
            # Pass message into some chain for processing...
            return chain(message)

        # Do not forget to run consumer loop 
        # in the main part of module later:
        # `run_asyn([amqp.consumer.create_tasks_future(), ...])`

    """

    mark_name = "consumer" #: alias for decorator 

    #: Keyword arguments for decorator
    decorator_kwargs = [
        "queue", 
        "queue_settings"
        ]

    #: Required keyword arguments for decorator
    decorator_required_kwargs = [
        "queue", 
        ]

    description = "Register AMQP consumer per one queue"
    
    #: Could be used mutiple times per one module
    once_per_module = False

    @classmethod
    def driver_factory(cls, args=None):
        "Should return driver instance (or connection pool instance)"
        # TODO: move from Driver to ConnectionPool
        import sys, argparse
        args = args or sys.argv[1:]
        parser = argparse.ArgumentParser()
        parser.add_argument('--amqp', required=True, help='Select AMQP mode')
        args = parser.parse_args(args)
        amqp_alias = args.amqp
        return AmqpDriver(amqp_alias)

    @classmethod
    def wrap_taskflow_item(cls, driver, entrypoint_item):
        "Awaitable for underlying consumer loop"
        callback = entrypoint_item.handler
        queue_name = entrypoint_item.meta["queue"]
        queue_settings = entrypoint_item.meta.get("queue_settings")
        queue_settings = ff.weld(queue_settings or {}, AmqpQueueTemplate.default_queue_settings())
        return AsyncAmqpConsumerLoop(
            driver, 
            callback, 
            queue_name=queue_name, 
            queue_settings=queue_settings)


@entities.register_decorator
class AmqpProducerDecorator(AsyncEndpoint, entrypoint.Transmitter):
    """Decorator to mark producer function. Function result becomes a message.

    Usage:

    .. code-block:: python

        @amqp.producer(exchange="fairways-out")
        def send_message(message):
            # You could return a simple string as a message body:
            return "Hello, World!"

        @amqp.producer(exchange="fws-out")
        def send_message_ext(message):
            # You could return dict with body and metadata:
            return dict(
                body="Hello, World!",
                headers={},
                routing_key="for.all.people"
            )

        # Do not forget to run producer loop 
        # in the main part of module later:
        # `run_asyn([amqp.producer.create_tasks_future(), ...])`

    """
    
    mark_name = "producer"
    decorator_kwargs = [
        "exchange", 
        "queue_settings"
        ]
    decorator_required_kwargs = [
        "exchange", 
        ]

    description = "Register AMQP producer per one exchange"
    once_per_module = False

    def __call__(self, subject):
        # Override inherited 
        f = entrypoint.Transmitter.__call__(self, subject)
        queue = asyncio.Queue()
        # TODO: use Queue registry mapped to callable instead of "dynamic attribute"
        subject.queue = queue
        loop = asyncio.get_event_loop()
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)
            asyncio.run_coroutine_threadsafe(queue.put(result), loop)
            # queue.put_nowait(result)
            log.debug("WRAPPER called, result: %s", result)
            return result
        return wrapper

    @classmethod
    def driver_factory(cls, args=None):
        "Should return driver instance (or connection pool instance)"
        import sys, argparse
        args = args or sys.argv[1:]
        parser = argparse.ArgumentParser()
        parser.add_argument('--amqp', required=True, help='Select AMQP mode')
        args = parser.parse_args(args)
        amqp_alias = args.amqp
        return AmqpDriver(amqp_alias)

    @classmethod
    def wrap_taskflow_item(cls, driver, entrypoint_item):
        # callback = entrypoint_item.handler
        queue_bus = entrypoint_item.handler.queue
        exchange_name = entrypoint_item.meta["exchange"]
        exchange_settings = entrypoint_item.meta.get("exchange_settings")
        exchange_settings = ff.weld(exchange_settings or {}, AmqpExchangeTemplate.default_exchange_settings())
        return AsyncAmqpProducerLoop(
            driver, 
            queue_bus, 
            exchange_name=exchange_name, 
            exchange_settings=exchange_settings)

