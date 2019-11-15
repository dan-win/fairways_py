from .base import (AsyncDataDriver, UriConnMixin)
# Should provice async methods .fetch, .execute

import asyncio
import aio_pika

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
    
    def on_message(self, queue_name, asyn_c: Callable):
        async def main_loop():
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
                log.error("AMQP operation error: {} at {};".format(e, params))
                raise
            finally:
                if self.autoclose:
                    await self.close()
        
        loop = asyncio.get_event_loop()
        connection = loop.run_until_complete(main_loop())

        loop.run_forever()        

