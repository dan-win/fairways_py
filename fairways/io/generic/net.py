""" Networking """
from .base import (BaseQuery, ReaderMixin, WriterMixin)

from .serde import (serialize_json, deserialize_json)
import pickle
import urllib.parse

from fairways.funcflow import FuncFlow as ff


class HttpQueryTemplate:
    """ Template for HTTP request.
    Note than all parameters should be used as named, e.g.:
    ```HttpQueryTemplate(url="http://127.0.0.1")```

    :param url: Request
    :type url: str
    :param method: HTTP request method, defaults to 'GET'
    :type method: str, optional
    :param content_type: Content-Type, defaults to 'application/x-www-form-urlencoded'
    :type content_type: str, optional
    :param headers: HTTP headers (except "Content-Type"), defaults to None
    :type headers: dict, optional
    :param stream: Use streaming, defaults to False
    :type stream: bool, optional
    :raises ValueError: Unknown Content-Type
    """

    # to-do: Make more stable solution to create hash (take into account complex cases like "application/json;charset=UTF-8", "text/json, etc."). Use regex to extract "root" part of context type descriptio

    #: Encoders registry
    encoders = {
        'text/plain': str,
        'application/json': serialize_json,
        'application/x-www-form-urlencoded': lambda d: urllib.parse.urlencode(d, quote_via=urllib.parse.quote)
    }
    
    # def __init__(self, **kwargs):
    #     """[summary]
    #     """
    #     self.method = kwargs.get('method', 'GET').lower()
    #     self.content_type = kwargs.get('content_type', 'application/x-www-form-urlencoded').lower()
    #     self._headers = kwargs.get('headers', {})
    #     self.url_template = kwargs['url']
    #     self.stream = kwargs.get('stream', False)

    def __init__(self, *, 
        method='GET', 
        content_type='application/x-www-form-urlencoded',
        headers=None,
        url,
        stream=False
        ):
        """Constructor method
        """

        self.method = method.lower()
        content_type = content_type.lower()
        self.content_type = content_type.split(';')[0] # Remove optional encoding portion like text/plain;utf-8
        if self.content_type not in self.encoders.keys():
            raise ValueError(f"Unknown content-type: {content_type}")
        self._headers = headers or {}
        self._headers.update({
            'Content-type': content_type
        })
        self.url_template = url
        self.stream = stream

    def _prepare_url(self, *path_args, **query_args):
        """Render URL using specified template, path and query arguments.

        \*path_args: Positional parameters for URL 
        \**query_args: Named parameters for a query part of URL        
        :return: URL
        :rtype: str
        """

        url = self.url_template.format(*path_args)
        if query_args:
            fmt_query = urllib.parse.urlencode(query_args, quote_via=urllib.parse.quote)
            url = f'{url}?{fmt_query}'
        return url
    
    def _prepare_body(self, data):
        """Assign request body and encode it.
        Body will be encoded in accordance with assigned "content_type".
        Body allowed for the following HTTP methods: POST, PUT, PATCH.

        :param data: Python data for encoding into request body.  
        :type data: str|Mapping
        :raises TypeError: Body not allowed for selected HTTP method
        :return: Serialized body
        :rtype: str
        """
        if data:
            if self.method in ('post', 'put', 'patch'):
                content_type = self.content_type
                encoder = self.encoders[content_type]
                encoded_data = encoder(data)
                self._headers.update({
                    'Content-length': str(len(encoded_data))
                })

                return encoded_data
            raise TypeError(f"Body not allowed for method: {self.method}")
            
    def _prepare_headers(self, encoded_data):
        result = self._headers.copy()
        return result
            
    def render(self, data, *path_args, **query_args):
        """Transform instance data and request data to keyword arguments for requests 
        
        :param data: Python data for encoding into request body.  
        :type data: str|Mapping
        
        \*path_args: Positional parameters for URL 
        \**query_args: Named parameters for a query part of URL 

        :return: Keyword arguments to pass them into Python requests getters
        :rtype: dict
        """

        encoded_data = self._prepare_body(data)

        rq_kwargs = dict(
            url = self._prepare_url(*path_args, **query_args),
            method = self.method,
        )

        headers = self._prepare_headers(encoded_data)
        if headers:
            rq_kwargs["headers"] = headers

        body = encoded_data
        if body:
            rq_kwargs["data"] = encoded_data

        if self.stream:
            rq_kwargs["stream"] = True

        return rq_kwargs



class HttpQuery(BaseQuery, ReaderMixin, WriterMixin):
    """HTTP request. Read/Write.

    :param template: Template to build resource-specific query for operation. It can contain parameters.
    :type template: HttpQueryTemplate
    :param connection_alias: HTTP host which exposes some service (e.g.: `http://ip-api.com`).
    :type connection_alias: str
    :param driver: Driver class. Use HttpDriver.
    :type driver: HttpDriver
    :param meta: Any user-defined data to store with this query, defaults to None
    :type meta: Mapping, optional

    Example:

    >>> conn_str = 'http://ip-api.com'
    >>> template = HttpQueryTemplate(
    ...        url="/{}/",
    ...        method='GET')
    >>> client = HttpQuery(template, conn_str, HttpDriver)
    >>> result = client.get_records(
    ...        path_args=['json'],
    ...        query_args=dict(fields='61439'),
    ...        data=None)
    >>> 'city' in result
    True 
    """
    
    #: Template class for HTTP request
    template_class = HttpQueryTemplate
    
    def _transform_params(self, params): # -> dict
        path_args = params.get("path_args", {})
        query_args = params.get("query_args", {})
        data = params.get("data", None)
        return self.template.render(data, *path_args, **query_args)


class HttpQueryParams:
    """Parameters for HTTP request 

    :param method: HTTP method
    :type method: str
    :param url: URL
    :type url: str
    :param headers: Request headers, defaults to None
    :type headers: dict, optional
    :param body: Optional body for request, defaults to None
    :type body: str, optional
    """
    def __init__(self, *,
        method,
        headers=None,
        url,
        body=None):
        """Constructor method
        """
        self.method = method
        self.headers = headers or {}
        self.url = url
        self.body = body

    # def __init__(self, **kwargs):
    #     self.method = kwargs['method']
    #     self.headers = kwargs.get('headers', {})
    #     self.url = kwargs['url']
    #     self.body = kwargs.get('body', None)
    
class RedisPopQuery(BaseQuery, ReaderMixin):
    """Redis request (RPOP, BRPOP).
    This is narrow implementation to use Redis as extract-only data stack.
    Use special driver RedisStack for such tasks.

    Note that for more generic operations we have Redis, RedisConsumer and RedisPublisher drivers.
    
    Example:

    >>> # Suppose we defined environment variable: 
    >>> # `REDIS_ENDPOINT=redis://localhost:6379`
    >>> redis_alias = 'REDIS_ENDPOINT'
    >>> STACK = RedisPopQuery(
    ...    "my/redis/key",
    ...    redis_alias,
    ...    fairways.io.syn.redis.RedisStack)
    >>> records = STACK.get_records()
    """

    #: Template for Redis request is a string
    template_class = str

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

class AmqpExchangeTemplate:
    """RabbitMQ/AMQP exchange template for publisher (producer).
    Note that the current implementation uses "clean" approach (applications should not create, modify or delete any RabbitMQ exchanges or queries, all these operations should be performed by RabbitMQ admin). 

    Please do not modify values of durable, auto_delete, internal, passive - they are present for `pika <https://pika.readthedocs.io/en/stable/>`_ or `aio-pika <https://aio-pika.readthedocs.io/>`_ which is used to perform actual operations.

    :param exchange_name: Name of RabbitMQ exchange
    :type exchange_name: str
    :param content_type: Content type of messages, defaults to 'text/plain'
    :type content_type: str, optional
    :param routing_key: Routing key for all messages, default to None
    :type routing_key: str, optional
    :param exchange_settings: Exchange settings to pass as keywords arguments to aio-pika declare_exchange, defaults to `AmqpExchangeTemplate.default.exchange_settings()`
    :type exchange_settings: dict, optional
    """

    encoders = {
        'text/plain': str,
        'application/json': serialize_json,
        'application/octet-stream': pickle.dumps,
    }

    def __init__(self, exchange_name, *,
            content_type=None,
            routing_key=None,
            exchange_settings=None,
            ):
        """Constructor method
        """
        self.exchange_name = exchange_name 
        self.exchange_settings = ff.weld(exchange_settings or {}, self.default_exchange_settings())
        self.content_type = content_type or 'text/plain'
        self.routing_key = routing_key or ""
    
    def render(self, *, 
            message,
            routing_key=None,
            content_type=None,
            headers=None,
            exchange_settings=None):

        routing_key = routing_key or self.routing_key
        content_type = content_type or self.content_type
        headers = headers or {}

        try:
            encoder = self.encoders[content_type]
        except:
            raise Exception(f"Unknown content-type: {content_type}")
        encoded_data = encoder(message)
        return dict(
            body=encoded_data,
            exchange=self.exchange_name, 
            routing_key=routing_key,
            headers=headers,
            content_type=content_type, 
            exchange_settings=self.exchange_settings)

    @staticmethod
    def default_exchange_settings():
        """Exchange settings to pass into aio-pika declare_exchange method
        
        :return: Default settings for exchange
        :rtype: dict
        """
        return dict(
            durable = True, # Durability (exchange survive broker restart)
            auto_delete = False, # Delete queue when channel will be closed
            internal = False, # Do not send it to broker just create an object
            passive = True, # Only check to see if the queue exists.
            timeout = None, # Execution timeout
        )

class AmqpQueueTemplate:
    """RabbitMQ/AMQP exchange template for subscriber (consumer).
    Note that the current implementation uses "clean" approach (applications should not create, modify or delete any RabbitMQ exchanges or queries, all these operations should be performed by RabbitMQ admin). 

    Please do not modify values of durable, auto_delete, exclusive, passive - they are present for `pika <https://pika.readthedocs.io/en/stable/>`_ or `aio-pika <https://aio-pika.readthedocs.io/>`_ which is used to perform actual operations.

    :param queue_name: RabbitMQ queue name
    :type queue_name: str
    :param content_type: Content type of messages, defaults to 'text/plain'
    :type content_type: str, optional
    :param queue_settings: Queue settings to pass as keywords arguments to aio-pika declare_queue, defaults to `AmqpQueueTemplate.default.queue_settings()`
    :type queue_settings: dict, optional
    """

    decoders = {
        'text/plain': str,
        'application/json': deserialize_json,
        'application/octet-stream': pickle.loads,
    }

    def __init__(self, queue_name, *,
        content_type = None,
        queue_settings = None,
        ):
        """Constructor method        
        """
        self.queue_name = queue_name
        self.queue_settings = ff.weld(queue_settings or {}, self.default_queue_settings())
        self.content_type = content_type or 'text/plain'

    def render(self, *, queue_name):
        return 
            # queue_name = params["queue"]
            # queue_settings = params.get("queue_settings", DEFAULT_QUEUE_SETTINGS)

        return dict(
            queue_name=queue_name,
            queue_settings=self.queue_settings,
            content_type=self.content_type
        )

    @staticmethod
    def default_queue_settings():
        """Queue settings to pass into aio-pika declare_exchange method
        
        :return: Default settings for queue
        :rtype: dict
        """
        return dict(
            durable = True, # Durability (exchange survive broker restart)
            auto_delete = False, # Delete queue when channel will be closed
            exclusive = False, # Exclusive queues may only be accessed by the current connection, and are deleted when that connection closes
            passive = True, # Only check to see if the queue exists.
            timeout = 5, # Execution timeout
        )

class AmqpPublishQuery(BaseQuery, WriterMixin):
    """AMQP publish request. Write operation.

    :param template: Template to build permanent part for operation logic. It can contain parameters.
    :type template: AmqpExchangeTemplate
    :param connection_alias: Name of environment/config variable which holds connection string (e.g.: `amqp://user:password@localhost:5672/%2f`).
    :type connection_alias: str
    :param driver: Driver class. Use appropriate driver for your application (either syn.amqp.AmqpDriver or asyn.amqp.AmqpDriver).
    :type driver: syn.amqp.AmqpDriver | asyn.amqp.AmqpDriver
    :param meta: Any user-defined data to store with this query, defaults to None
    :type meta: Mapping, optional

    >>> # Suppose we defined environment variable: 
    >>> # `AMQP_ENDPOINT=amqp://user:password@localhost:5672/%2f`
    >>> conn_alias = 'AMQP_ENDPOINT'
    >>> pub_options = AmqpExchangeTemplate(
    ...            exchange_name="fairways")
    >>> test_publisher = AmqpPublishQuery(
    ...    pub_options, conn_alias, AmqpDriver, {})
    >>> test_publisher.execute(message="Hello, world!")
    """

    #: Template class for AMQP exchange
    template_class = AmqpExchangeTemplate

    def _transform_params(self, params): # -> dict
        return self.template.render(**params)

class AmqpConsumeQuery(BaseQuery, ReaderMixin):
    """AMQP consume request. Read operation. 

    :param template: Template to build permanent part for operation logic. It can contain parameters.
    :type template: AmqpQueueTemplate
    :param connection_alias: Name of environment/config variable which holds connection string (e.g.: `amqp://user:password@localhost:5672/%2f`).
    :type connection_alias: str
    :param driver: Driver class. Use appropriate driver for your application (either syn.amqp.AmqpDriver or asyn.amqp.AmqpDriver).
    :type driver: syn.amqp.AmqpDriver or asyn.amqp.AmqpDriver
    :param meta: Any user-defined data to store with this query, defaults to None
    :type meta: Mapping, optional

    >>> # Suppose we defined environment variable: 
    >>> # `AMQP_ENDPOINT=amqp://user:password@localhost:5672/%2f`
    >>> conn_alias = 'AMQP_ENDPOINT'
    >>> options = AmqpQueueTemplate(
    ...    queue_name="fairways")
    >>> consumer = AmqpConsumeQuery(
    ...    options, conn_alias, AmqpDriver)
    >>> result = consumer.get_records()
    """
    template_class = AmqpQueueTemplate

    def _transform_params(self, params): # -> dict
        # return dict(options=self.template)
        return self.template.render(**params)
