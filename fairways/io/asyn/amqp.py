from .base import (AsyncDataDriver, UriConnMixin)
# Should provice async methods .fetch, .execute

import asyncio
import aio_pika

from fairways.ci.helpers import run_asyn
from fairways.decorators import (entities, entrypoint)

import logging
log = logging.getLogger(__name__)

from typing import Callable

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

            try:
                await self._ensure_connection()
                connection = self.engine
                channel = await connection.channel()    # type: aio_pika.Channel            

                exchange = await channel.declare_exchange(exchange_name, **exchange_settings)

                log.debug("Sending AMQP message")

                await exchange.publish(
                    aio_pika.Message(
                        body=message.encode()
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

    async def consume(self, asyn_c: Callable, **params):
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

        except Exception as e:
            log.error("AMQP operation error: {} at {};".format(e, queue_name))
            raise
        finally:
            if self.autoclose:
                await self.close()
        

    def on_message(self, asyn_c: Callable, **params):
        run_asyn(self.consume(asyn_c, **params))

@entities.register_decorator
class Amqp(entrypoint.Listener):
    mark_name = "amqp"
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

        def run_consumer(driver, entrypoint_item):
            callback = entrypoint_item.handler
            queue_name = entrypoint_item.meta["queue"]
            queue_settings = entrypoint_item.meta.get("queue_settings", DEFAULT_QUEUE_SETTINGS)
            return driver.on_message(callback, queue=queue_name, queue_settings=queue_settings)

        args = args or sys.argv
        parser = argparse.ArgumentParser()
        parser.add_argument('--amqp', required=True, help='Select AMQP mode')
        args = parser.parse_args(args)
        amqp_alias = args.amqp


        items_to_run = cls.items()
        if not items_to_run:
            raise ValueError("Cannot find amqp entrypoints")
        
        driver = AmqpDriver(amqp_alias)

        tasks = asyncio.gather([
            run_consumer(driver, item)
            for item in items_to_run
        ])
        
        own_loop = None
        if new_loop:
            own_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(own_loop)
            loop = own_loop
        else:
            loop = asyncio.get_event_loop()
        try:
            # Note that "gather" wraps results into list:
            (result,) = loop.run_until_complete(tasks)
            return result
        finally:
            if own_loop:
                own_loop.close()
