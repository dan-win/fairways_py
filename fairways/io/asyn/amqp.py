from .base import (AsyncDataDriver, UriConnMixin, AsyncEndpoint)
# Should provice async methods .fetch, .execute
from fairways.io.asyn.base import AsyncLoop

import asyncio
import aio_pika

from fairways.ci.helpers import run_asyn
from fairways.decorators import (entities, entrypoint)

import logging
log = logging.getLogger(__name__)

DEFAULT_EXCHANGE_SETTINGS = dict(
    durable = True, 
    auto_delete = False,
    internal = False, 
    passive = True,    
)

DEFAULT_QUEUE_SETTINGS = dict(
    durable = True, 
    auto_delete = False,
    exclusive = False,
    passive = True,    
)

class AmqpDriver(AsyncDataDriver, UriConnMixin):
    default_conn_str = "amqp://guest:guest@localhost:5672/%2f"
    autoclose = True

    def is_connected(self):
        return self.engine is not None

    async def _connect(self):
        conn_str = self.conn_str
        engine = await aio_pika.connect(conn_str)
        self.engine = engine

    async def close(self):
        if self.is_connected():
            await self.engine.close()
            self.engine = None

    def execute(self, _, **params):

        async def push():
            exchange_name = params["exchange"]
            exchange_settings = params.get("exchange_settings", DEFAULT_EXCHANGE_SETTINGS)
            routing_key = params.get("routing_key") or ""
            message = params["body"]
            headers = params.get("headers", {})

            try:
                await self._ensure_connection()
                connection = self.engine
                channel = await connection.channel()    # type: aio_pika.Channel            

                exchange = await channel.declare_exchange(exchange_name, **exchange_settings)

                log.debug("Sending AMQP message")

                if isinstance(message, str):
                    message=message.encode()
                elif isinstance(message, bytes):
                    pass # Ok
                else:
                    raise Exception(f"Unsupported type of message: {type(message)}")

                await exchange.publish(
                    aio_pika.Message(
                        body=message,
                        headers=headers,
                    ),
                    routing_key=routing_key
                )

            except Exception as e:
                log.error("AMQP operation error: {} at {};".format(e, params))
                raise
            finally:
                if self.autoclose:
                    await self.close()
        
        return push()


    def get_records(self, _, **params):

        async def pull():
            queue_name = params["queue"]
            queue_settings = params.get("queue_settings", DEFAULT_QUEUE_SETTINGS)

            try:
                await self._ensure_connection()
                connection = self.engine
                channel = await connection.channel()    # type: aio_pika.Channel

                await channel.set_qos(prefetch_count=1)

                queue = await channel.declare_queue(queue_name, **queue_settings)

                log.debug("Receiving AMQP message")

                incoming_message = await queue.get(timeout=5, fail=False)
                if incoming_message is not None:
                    return [incoming_message]
                return []

                # async with queue.iterator() as queue_iter:
                #     async for message in queue_iter:
                #         async with message.process():
                #             return message

            except Exception as e:
                log.error("AMQP operation error: {} at {};".format(e, params))
                raise
            finally:
                if self.autoclose:
                    await self.close()
        
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
        run_asyn(self._consume_asyn(asyn_c, **params))

    async def message_stream(self, **params):
        queue_name = params["queue"]
        queue_settings = params.get("queue_settings", DEFAULT_QUEUE_SETTINGS)

        await self._ensure_connection()
        connection = self.engine
        channel = await connection.channel()    # type: aio_pika.Channel

        await channel.set_qos(prefetch_count=1)

        queue = await channel.declare_queue(queue_name, **queue_settings)

        log.debug("Starting AMQP consumer loop")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    yield message
                    await asyncio.sleep(0.1)


class AsyncAmqpConsumerLoop(AsyncLoop):

    def __init__(self, driver_instance, decorated_task, **params):
        super().__init__()
        self.driver_instance = driver_instance
        self.decorated_task = decorated_task
        self.params = params
        

    async def _input_stream(self):
        """
        This method should be redefined in descendants. 
        This sample is for demo purposes only
        """
        params = self.params
        async for message in self.driver_instance.message_stream(**params):
            yield message

    async def _output_stream(self, message):
        """
        This method should be redefined in descendants. 
        This sample is for demo purposes only"""
        # print('relaying {}'.format(message))
        # log.debug(f'{str(self)} relaying message')

        loop = asyncio.get_event_loop()

        # 1. Run in the default loop's executor:
        result = await loop.run_in_executor(
            None, self.decorated_task, message)
        # log.debug(f'default thread pool: {result}')
        

class AsyncAmqpProducerLoop(AsyncLoop):

    def __init__(self, driver_instance, queue_bus, **params):
        super().__init__()
        self.driver_instance = driver_instance
        self.queue_bus = queue_bus
        self.params = params
        
    async def _input_stream(self):
        """
        Read messages from input queue
        """
        log.debug("Entering input stream... %s", self.queue_bus)
        queue = self.queue_bus
        while True:
            item = await queue.get()
            log.debug("Message in _input_stream...")
            queue.task_done()
            yield item

        # params = self.params
        # async for message in self.driver_instance.message_stream(**params):
        #     yield message

    async def _output_stream(self, message):
        """
        """
        # print('relaying {}'.format(message))
        log.warn(f'{str(self)} relaying message')

        if isinstance(message, (str, bytes)):
            params = dict(body=message)
        elif isinstance(message, dict):
            params = message
        else:
            raise TypeError(f"AmqpPublisher cannot relay this type of message: {type(message)}")
        # MOVE TO POOL!!!!!!!!!!!!!!!!!!!!!!
        # print("What I got: ", message)
        try:
            await self.driver_instance.execute(None,
                exchange=self.params["exchange"],
                exchange_settings=self.params["exchange_settings"],
                **params)
            # print("MESSAGE PUBLISHED TO AMQP")
        except Exception as e:
            log.error("AMQP error: %s", e)

        # loop = asyncio.get_event_loop()

        # # 1. Run in the default loop's executor:
        # result = await loop.run_in_executor(
        #     None, self.decorated_task, message)
        # print('default thread pool', result)


@entities.register_decorator
class AmqpConsumerDecorator(AsyncEndpoint, entrypoint.Listener):
    mark_name = "consumer"
    decorator_kwargs = [
        "queue", 
        "queue_settings"
        ]
    decorator_required_kwargs = [
        "queue", 
        ]

    description = "Register AMQP consumer per one queue"
    once_per_module = False

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
    def wrap_taskflow_item(cls, driver, entrypoint_item, loop):
        callback = entrypoint_item.handler
        queue_name = entrypoint_item.meta["queue"]
        queue_settings = entrypoint_item.meta.get("queue_settings", DEFAULT_QUEUE_SETTINGS)
        return AsyncAmqpConsumerLoop(driver, callback, queue=queue_name, queue_settings=queue_settings)


#

@entities.register_decorator
class AmqpProducerDecorator(AsyncEndpoint, entrypoint.Transmitter):
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

    # def __init__(self, *args, **kwargs):
    #     entrypoint.Transmitter.__init__(self, *args, **kwargs)
    #     self.queue = asyncio.Queue()

    def __call__(self, subject):
        # Override inherited 
        f = entrypoint.Transmitter.__call__(self, subject)
        queue = asyncio.Queue()
        # find meta record for subject:
        subject.queue = queue
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)
            queue.put_nowait(result)
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
    def wrap_taskflow_item(cls, driver, entrypoint_item, loop):
        # callback = entrypoint_item.handler
        queue_bus = entrypoint_item.handler.queue
        exchange_name = entrypoint_item.meta["exchange"]
        exchange_settings = entrypoint_item.meta.get("exchange_settings", DEFAULT_EXCHANGE_SETTINGS)
        return AsyncAmqpProducerLoop(driver, queue_bus, exchange=exchange_name, exchange_settings=exchange_settings)

