from .base import (AsyncDataDriver, UriConnMixin)
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


class AsyncAmqpLoop(AsyncLoop):

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
        print(f'{str(self)} relaying {message}')

        loop = asyncio.get_event_loop()

        # 1. Run in the default loop's executor:
        result = await loop.run_in_executor(
            None, self.decorated_task, message)
        print('default thread pool', result)
        


@entities.register_decorator
class Amqp(entrypoint.Listener):
    mark_name = "entrypoint"
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
    def run(cls, args=None, new_loop=True):
        import sys, argparse
        import signal
        import functools
        from contextlib import suppress

        async def shutdown(sig, loop):
            print('caught {0}'.format(sig.name))
            tasks = [task for task in asyncio.Task.all_tasks() if task is not 
                    asyncio.tasks.Task.current_task()]
            print(tasks)
            for task in tasks:
                task.cancel()
                with suppress(asyncio.CancelledError):
                    print('suppressed error')
                    await task
            results = await asyncio.gather(*tasks, return_exceptions=True)
            print('finished awaiting cancelled tasks, results: {0}'.format(results))
            loop.stop()

        # def run_consumer(driver, entrypoint_item):
        #     callback = entrypoint_item.handler
        #     queue_name = entrypoint_item.meta["queue"]
        #     queue_settings = entrypoint_item.meta.get("queue_settings", DEFAULT_QUEUE_SETTINGS)
        #     # return driver.consume(callback, queue=queue_name, queue_settings=queue_settings)
        #     return driver._consume_asyn(callback, queue=queue_name, queue_settings=queue_settings)

        def create_consumer(driver, entrypoint_item):
            callback = entrypoint_item.handler
            queue_name = entrypoint_item.meta["queue"]
            queue_settings = entrypoint_item.meta.get("queue_settings", DEFAULT_QUEUE_SETTINGS)
            # return driver.consume(callback, queue=queue_name, queue_settings=queue_settings)
            # return driver._consume_asyn(callback, queue=queue_name, queue_settings=queue_settings)
            return AsyncAmqpLoop(driver, callback, queue=queue_name, queue_settings=queue_settings)

        args = args or sys.argv
        parser = argparse.ArgumentParser()
        parser.add_argument('--amqp', required=True, help='Select AMQP mode')
        args = parser.parse_args(args)
        amqp_alias = args.amqp


        items_to_run = cls.items()
        if not items_to_run:
            raise ValueError("Cannot find amqp entrypoints")
        
        driver = AmqpDriver(amqp_alias)
        
        loop = asyncio.get_event_loop()
        # asyncio.set_event_loop(loop)

        print("======================1")
        tasks = asyncio.gather(*[
            # run_consumer(driver, item)
            create_consumer(driver, item).run(loop)
            for item in items_to_run
        ], loop=loop)
        print("======================2")

        print("======================3")

        # signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
        # for s in signals:
        #     loop.add_signal_handler(
        #         s, lambda: asyncio.ensure_future(shutdown(s, loop)))

        print("======================4")
        try:
            log.debug("Jumping into loop")
            # Note that "gather" wraps results into list:
            result = loop.run_until_complete(tasks)
            # return result
            log.debug("Exiting: %r", result)

            # Wait for pending tasks:
            pending = asyncio.Task.all_tasks()
            print("Pending:", pending)
            print("======================5")
            loop.run_until_complete(asyncio.gather(*pending))
            print("======================6")

        # except KeyboardInterrupt:  # pragma: no branch
        #     pass
        finally:

            result = loop.run_until_complete(driver.close())
            log.debug("Driver closed: %r", result)
            # loop.close()
