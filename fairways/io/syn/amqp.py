
from .base import (SynDataDriver, UriConnMixin)
# Should provice async methods .fetch, .execute

from fairways.io.generic.net import (
    AmqpQueueTemplate,
    AmqpExchangeTemplate
)

from collections import namedtuple

import pika
from fairways.decorators import (entities, entrypoint)
import time

from typing import (List)

import logging
log = logging.getLogger(__name__)

# DEFAULT_EXCHANGE_SETTINGS = dict(
#     durable = True, 
#     auto_delete = False,
#     internal = False, 
#     passive = True,    
# )

DEFAULT_QUEUE_SETTINGS = dict(
    durable = True, 
    auto_delete = False,
    exclusive = False,
    passive = True,    
)

Message = namedtuple("Message", "body,header,method".split(","))

class AmqpDriver(SynDataDriver, UriConnMixin):
    """AMQP/RabbitMQ driver.
    Requires `pika <https://pika.readthedocs.io/en/stable/>`_.
    
    :param env_varname: Name of enviromnent variable (or settings attribute) which holds connection string (e.g.: "mysql://user@pass@host/db")
    :type env_varname: str
    """

    #: Default connection string (for testing)
    default_conn_str = "amqp://guest:guest@localhost:5672/%2f"

    #: Do not close connection after single request
    autoclose = False

    def is_connected(self):
        return self.engine is not None and not self.engine.is_open

    def _connect(self):
        conn_str = self.conn_str
        parameters = pika.URLParameters(conn_str)
        engine = pika.BlockingConnection(parameters)
        self.engine = engine

    def close(self):
        if self.is_connected():
            self.engine.close()
            self.engine = None

    def execute(self, _, *, 
        message, 
        routing_key="", 
        options):

        """Publish message.
        
        :param _: Ignored (only for consistency with BaseDriver signature)
        :type _: Any
        :raises Exception: Re-raise exceptions of underlying engine
        """
        # TODO: 
        message = params["message"]        
        routing_key = params["routing_key"]
        options = params["options"]
        # exchange_settings = params.get("exchange_settings", DEFAULT_EXCHANGE_SETTINGS)
        exchange_name = options.exchange_name
        content_type = options.content_type

        try:
            self._ensure_connection()
            connection = self.engine
            channel = connection.channel()    # type: aio_pika.Channel            
            # exchange = await channel.declare_exchange(exchange_name, **exchange_settings)

            log.debug("Sending AMQP message")

            channel.basic_publish(exchange_name,
                    routing_key,
                    message,
                    pika.BasicProperties(content_type=content_type,
                                        delivery_mode=1))

        except Exception as e:
            log.error("AMQP operation error: {} at {};".format(e, params))
            raise
        finally:
            if self.autoclose:
                self.close()


    def get_records(self, _, **params) -> List[Message]:
        """Fetch single message
        
        :param _: Ignored (only for consistency with BaseDriver signature)
        :type _: Any
        :return: Message
        :rtype: List[Message] 
        """

        options = params["options"]
        # queue_settings = params.get("queue_settings", DEFAULT_QUEUE_SETTINGS)
        try:
            self._ensure_connection()
            connection = self.engine
            channel = connection.channel()    # type: aio_pika.Channel            

            # queue = await channel.declare_queue(queue_name, **queue_settings)

            method_frame, header_frame, body = channel.basic_get(options.queue_name)
            if method_frame:
                channel.basic_ack(method_frame.delivery_tag)
                # log.warning("Getting JSON??? ******************* %s| %s| %s", method_frame, header_frame, body)
                # log.warning("Getting JSON??? ******************* %s| %s| %s",header_frame.content_type,header_frame.content_encoding,header_frame.headers)
                return [Message(body=body, header=header_frame, method=method_frame)]
            else:
                log.debug('No message returned')
                return []

            log.debug("Receiving AMQP message")

        except Exception as e:
            log.error("AMQP operation error: %r at %s;", e, params)
            raise
        finally:
            if self.autoclose:
                self.close()
        

    def consume(self, callback, **params):
        queue_name = params["queue"]
        queue_settings = params.get(
            "queue_settings", DEFAULT_QUEUE_SETTINGS)
        def cb_wrapper(channel, method, properties, body):
            callback(body)
            time.sleep(0.1)

        try:
            # self._ensure_connection()
            # connection = self.engine
            # channel = connection.channel()    # type: aio_pika.Channel

            log.warning("Starting AMQP consumer loop")

            while True:
                # Note this loop for re-connection only!
                try:
                    self.close()
                    self._ensure_connection()
                    connection = self.engine
                    # connection = pika.BlockingConnection()
                    channel = connection.channel()
                    channel.basic_consume(queue_name, cb_wrapper)
                    channel.start_consuming()
                # Don't recover if connection was closed by broker
                except pika.exceptions.ConnectionClosedByBroker:
                    break
                # Don't recover on channel errors
                except pika.exceptions.AMQPChannelError:
                    break
                # Recover on all other connection errors
                except pika.exceptions.AMQPConnectionError:
                    continue


        except Exception as e:
            log.error("AMQP operation error: {} at {};".format(e, queue_name))
            raise
        finally:
            if self.autoclose:
                self.close()
        

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
        import sys, argparse, functools, uuid
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def run_consumer(driver, entrypoint_item):
            callback = entrypoint_item.handler
            queue_name = entrypoint_item.meta["queue"]
            print("Instance: ", uuid.uuid4(), queue_name)
            queue_settings = entrypoint_item.meta.get("queue_settings", DEFAULT_QUEUE_SETTINGS)
            return driver.consume(callback, queue=queue_name, queue_settings=queue_settings)

        args = args or sys.argv
        parser = argparse.ArgumentParser()
        parser.add_argument('--amqp', required=True, help='Select AMQP mode')
        args = parser.parse_args(args)
        amqp_alias = args.amqp


        items_to_run = cls.items()
        if not items_to_run:
            raise ValueError("Cannot find amqp entrypoints")
        
        driver = AmqpDriver(amqp_alias)

        futures = []

        with ThreadPoolExecutor(max_workers=None) as executor:
            executor.map(functools.partial(run_consumer, driver), items_to_run)
        #     for item in items_to_run:
        #         futures.append(executor.submit(run_consumer, driver, item))

        # for f in as_completed(futures):
        #     if f.exception() is not None:
        #         print(f.exception())


"""
parameters = pika.URLParameters('amqp://guest:guest@localhost:5672/%2F')

connection = pika.BlockingConnection(parameters)

channel = connection.channel()

channel.basic_publish('test_exchange',
                      'test_routing_key',
                      'message body value',
                      pika.BasicProperties(content_type='text/plain',
                                           delivery_mode=1))

connection.close()
"""