from .base import (BaseQuery, ReaderMixin, WriterMixin)

from .serde import (serialize_json, deserialize_json)
import pickle
import urllib.parse


class HttpQueryTemplate:

    # NOTE: Make more stable solution to create hash (take into account complex cases like "application/json;charset=UTF-8", "text/json, etc."). Use regex to extract "root" part of context type descriptio
    encoders = {
        'application/json': serialize_json,
        'application/x-www-form-urlencoded': lambda d: urllib.parse.urlencode(d, quote_via=urllib.parse.quote)
    }
    
    def __init__(self, **kwargs):
        self.method = kwargs.get('method', 'GET').lower()
        self.content_type = kwargs.get('content_type', 'application/x-www-form-urlencoded').lower()
        self._headers = kwargs.get('headers', {})
        self.url_template = kwargs['url']
        self.stream = kwargs.get('stream', False)
    
    def url(self, *path_args, **query_args):
        """Url formatted from template and data supplied
        
        Returns:
            [str] -- [Url]
        """
        url = self.url_template.format(*path_args)
        if query_args:
            fmt_query = urllib.parse.urlencode(query_args, quote_via=urllib.parse.quote)
            url = f'{url}?{fmt_query}'
        return url
    
    def body(self, data):
        if data:
            if self.method in ('post', 'put', 'patch'):
                content_type = self.content_type
                try:
                    encoder = self.encoders[content_type]
                except:
                    raise Exception(f"Unknown content-type: {content_type}")
                return encoder(data)
    
            raise Exception(f"Body not allowed for method: {self.method}")
            
    def headers(self, encoded_data):
        result = self._headers.copy()
        if encoded_data:
            if self.method in ('post', 'put', 'patch'):
                result.update({
                    'Content-type': self.content_type,
                    'Content-length': str(len(encoded_data))
                })
        return result
            
    def render(self, data, *path_args, **query_args):
        encoded_data = self.body(data)

        rq_kwargs = dict(
            url = self.url(*path_args, **query_args),
            method = self.method,
        )

        headers = self.headers(encoded_data)
        if headers:
            rq_kwargs["headers"] = headers

        body = encoded_data
        if body:
            rq_kwargs["data"] = encoded_data

        if self.stream:
            rq_kwargs["stream"] = True

        return rq_kwargs



class HttpQuery(BaseQuery, ReaderMixin, WriterMixin):
    template_class = HttpQueryTemplate
    
    def _transform_params(self, params): # -> dict
        path_args = params.get("path_args", {})
        query_args = params.get("query_args", {})
        data = params.get("data", None)
        return self.template.render(data, *path_args, **query_args)


class HttpQueryParams:

    def __init__(self, **kwargs):
        self.method = kwargs['method']
        self.headers = kwargs.get('headers', {})
        self.url = kwargs['url']
        self.body = kwargs.get('body', None)
    
class RedisPopQuery(BaseQuery, ReaderMixin):
    template_class = str

# DEFAULT_EXCHANGE_SETTINGS = dict(
#     durable = True, 
#     auto_delete = False,
#     internal = False, 
#     passive = True,    
#     content_type = 'text/plain'
# )

class AmqpExchangeTemplate:

    def __init__(self, exchange_name,
        durable = True, 
        auto_delete = False,
        internal = False, 
        passive = True,    
        content_type = 'text/plain'
        ):
        self.exchange_name = exchange_name 
        self.durable = durable
        self.auto_delete = auto_delete
        self.internal = internal
        self.passive = passive
        self.content_type = content_type


# DEFAULT_QUEUE_SETTINGS = dict(
#     durable = True, 
#     auto_delete = False,
#     exclusive = False,
#     passive = True,    
# )

class AmqpQueueTemplate:
    def __init__(self, queue_name,
        durable = True, 
        auto_delete = False,
        exclusive = False,
        passive = True,    
        content_type = 'text/plain'
        ):
        self.queue_name = queue_name
        self.durable = durable
        self.auto_delete = auto_delete
        self.exclusive = exclusive
        self.passive = passive
        self.content_type = content_type


class AmqpPublishQuery(BaseQuery, WriterMixin):
    template_class = AmqpExchangeTemplate

    encoders = {
        'application/json': serialize_json,
        'text/plain': str,
        'application/octet-stream': pickle.dumps,
    }

    def _transform_params(self, params): # -> dict
        message = params["message"]
        routing_key = params.get("routing_key", "")
        content_type = self.template.content_type
        try:
            encoder = self.encoders[content_type]
        except:
            raise Exception(f"Unknown content-type: {content_type}")
        encoded_data = encoder(message)
        return dict(message=encoded_data, routing_key=routing_key, options=self.template)

class AmqpConsumeQuery(BaseQuery, ReaderMixin):
    template_class = AmqpQueueTemplate

    decoders = {
        'application/json': deserialize_json,
        'text/plain': str,
        'application/octet-stream': pickle.loads,
    }

    def _transform_params(self, params): # -> dict
        return dict(options=self.template)
