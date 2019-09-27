import json
import urllib.parse

class HttpQueryParams:

    def __init__(self, **kwargs):
        self.method = kwargs.get('method', 'GET').lower()
        self.content_type = kwargs.get('content_type', 'application/x-www-form-urlencoded').lower()
        self.headers = kwargs.get('headers', {})
        self.url = kwargs['url']
        self.body = kwargs.get('body', None)
    

class HttpQueryTemplate:

    encoders = {
        'application/json': json.dumps,
        'application/x-www-form-urlencoded': lambda d: urllib.parse.urlencode(d, quote_via=urllib.parse.quote)
    }
    
    def __init__(self, **kwargs):
        self.method = kwargs.get('method', 'GET').lower()
        self.content_type = kwargs.get('content_type', 'application/x-www-form-urlencoded').lower()
        self.headers = kwargs.get('headers', {})
        self.url_template = kwargs['url']
    
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
                try:
                    content_type = self.content_type
                    encoder = self.encoders[content_type]
                    return encoder(data)
                except:
                    raise Exception(f"Unknown content-type: {content_type}")
            raise Exception(f"Body not allowed for method: {self.method}")
            
    
    def render(self, data, *path_args, **query_args):
        return dict(
            method = self.method,
            content_type = self.content_type,
            headers = self.headers,
            url = self.url(*path_args, **query_args),
            body = self.body(data)
        )
