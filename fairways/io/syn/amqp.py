
from .base import (SynDataDriver, UriConnMixin)
# Should provice async methods .fetch, .execute

from collections import namedtuple

import pika

import logging
log = logging.getLogger(__name__)

# DEFAULT_EXCHANGE_SETTINGS = dict(
#     durable = True, 
#     auto_delete = False,
#     internal = False, 
#     passive = True,    
# )

# DEFAULT_QUEUE_SETTINGS = dict(
#     durable = True, 
#     auto_delete = False,
#     exclusive = False,
#     passive = True,    
# )

Message = namedtuple("Message", "body,header,method".split(","))

class AmqpDriver(SynDataDriver, UriConnMixin):
    default_conn_str = "amqp://guest:guest@localhost:5672/%2f"
    autoclose = True

    def is_connected(self):
        return self.engine is not None

    def _connect(self):
        conn_str = self.conn_str
        parameters = pika.URLParameters(conn_str)
        engine = pika.BlockingConnection(parameters)
        self.engine = engine

    def close(self):
        if self.is_connected():
            self.engine.close()
            self.engine = None

    def execute(self, _, **params):
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


    def get_records(self, _, **params):

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
                return Message(body=body, header=header_frame, method=method_frame)
            else:
                print('No message returned')

            log.debug("Receiving AMQP message")

        except Exception as e:
            log.error("AMQP operation error: {} at {};".format(e, params))
            raise
        finally:
            if self.autoclose:
                self.close()
        


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