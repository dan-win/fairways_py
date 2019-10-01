import unittest
import unittest.mock

def setUpModule():
    pass

def tearDownModule():
    pass

class HttpMockTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from fairways.ci import helpers
        cls.helpers = helpers

        import fairways.io.generic
        from fairways.io.generic import net
        from fairways.io.syn.http import Http

        cls.net = net
        cls.driver = Http 

        import re
        import os

        cls.os = os

        root = helpers.getLogger()

    @classmethod
    def tearDownClass(cls):
        pass

    def test_request(self):
        """
        """
        HttpDriver = self.driver 

        HttpQuery = self.net.HttpQuery
        HttpQueryTemplate = self.net.HttpQueryTemplate

        os = self.os

        # default=":memory:"
        conn_alias = __name__

        test_message = "MY MESSAGE"

        host2 = 'http://{$username}:{$password}@test-api.com:8989/root'
        # http://ip-api.com/json/?fields=61439

        def request_mock(*args, **kwargs):
            "replace requests.get method"
            class MockResponse:
                def raise_for_status(self): 
                    pass
                def json(self): 
                    return dict(
                        request_args=self.request_args,
                        request_kwargs=self.request_kwargs
                    )
                def text(self):
                    return "Mock response"
                def __init__(self, request_args, request_kwargs):
                    self.request_args = request_args
                    self.request_kwargs = request_kwargs
                
            return MockResponse(args, kwargs)
        
        mock_environ = {
            conn_alias: host2, 
            "username":"myuser",
            "password":"mypassword"}

        HttpDriver.set_config_provider(os.environ)

        with unittest.mock.patch.dict('os.environ', mock_environ, clear=True):

            template = HttpQueryTemplate(
                url="/{}/",
                method='GET',
                content_type='application/json',
            )

            client = HttpQuery(template, conn_alias, HttpDriver)

            with unittest.mock.patch('requests.get', side_effect=request_mock):
                result = client.get_records(
                    path_args=['json'],
                    query_args=dict(fields='61439'),
                    data=None,
                )

        correct_url = 'http://test-api.com:8989/json/?fields=61439'
        
        self.assertEqual(result["request_args"], (correct_url,))

        print(f"RESPONDE *** {result['request_args']}; {result['request_kwargs']}")

        auth_obj = result["request_kwargs"]["auth"]

        self.assertEqual(auth_obj.username, "myuser")
        self.assertEqual(auth_obj.password, "mypassword")
