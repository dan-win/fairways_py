import unittest
import unittest.mock

def setUpModule():
    pass

def tearDownModule():
    pass

class HttpTestCase(unittest.TestCase):
    conn_str = "http://localhost:6370"

    # @classmethod
    # def clean_test_db(cls):
    #     import os
    #     if os.path.exists(cls.conn_str):
    #         os.remove(cls.conn_str)

    @classmethod
    def setUpClass(cls):
        from fairways.ci import helpers
        cls.helpers = helpers

        from fairways.io.generic import types #import HttpQueryTemplate
        from fairways.io.sync.http import Http
        from fairways.io.generic.dbi import HttpQuery

        cls.types = types
        cls.driver = Http 
        cls.query = HttpQuery

        import re
        import os

        # cls.clean_test_db()

        root = helpers.getLogger()

    @classmethod
    def tearDownClass(cls):
        # cls.clean_test_db()
        pass

    def test_consume(self):
        """
        """
        HttpDriver = self.driver 
        HttpQuery = self.query 

        HttpQueryTemplate = self.types.HttpQueryTemplate

        # default=":memory:"
        conn_alias = "MY_HTTP_CONN"

        test_message = "MY MESSAGE"

        host2 = 'http://ip-api.com'
        # http://ip-api.com/json/?fields=61439

        with unittest.mock.patch.dict('os.environ', {conn_alias: host2}, clear=True):

            template = HttpQueryTemplate(
                url="/{}/",
                method='GET',
            )

            client = HttpQuery(template, conn_alias, HttpDriver)

            result = client.get_records(
                path_args=['json'],
                query_args=dict(fields='61439'),
                data=None,
            )

        print(f"response: {result}")
        self.assertTrue(isinstance(result, dict))        
        self.assertTrue('city' in result)