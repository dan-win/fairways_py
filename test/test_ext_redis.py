import unittest
import unittest.mock

def setUpModule():
    pass

def tearDownModule():
    pass

class RedisPublishConsumeTestCase(unittest.TestCase):
    # conn_str = "redis://localhost:6370"
    conn_str = "unix:///home/dmitriy/docker-sockets/atacama_cache/redis.sock"

    # @classmethod
    # def clean_test_db(cls):
    #     import os
    #     if os.path.exists(cls.conn_str):
    #         os.remove(cls.conn_str)

    @classmethod
    def setUpClass(cls):
        from fairways.ci import helpers
        cls.helpers = helpers

        from fairways.io.asyn.consumer import redis

        from fairways.io.asyn.publisher import redis as redis_pub

        import asyncio
        import time
        import concurrent.futures
        import re
        import os
        cls.asyncio = asyncio
        cls.time = time
        cls.futures = concurrent.futures
        cls.re = re

        cls.redis = redis

        cls.redis_pub = redis_pub

        # cls.clean_test_db()

        root = helpers.getLogger()

    @classmethod
    def tearDownClass(cls):
        # cls.clean_test_db()
        pass

    def test_consume(self):
        """
        """
        asyncio = self.asyncio

        RedisConsumer = self.redis.RedisConsumer
        RedisDriver = self.redis.RedisDriver

        RedisPublisher = self.redis_pub.RedisPublisher

        # default=":memory:"
        db_alias = "MY_REDIS_CONN"

        test_message = "MY MESSAGE"

        with unittest.mock.patch.dict('os.environ', {db_alias: self.conn_str}, clear=True):

            pub_options = dict(
                command="RPUSH",
                key="TEST_KEY",
            )

            test_publisher = RedisPublisher(pub_options, db_alias, RedisDriver, {})
            self.helpers.run_asyn(test_publisher.execute(message=test_message))

            options = dict(
                command="BRPOP",
                key="TEST_KEY",
                kwargs=dict(timeout=10,encoding='utf-8')
            )
            consumer = RedisConsumer(options, db_alias, RedisDriver, {})

            result = self.helpers.run_asyn(consumer.get_records())

        self.assertEqual(result, [b'TEST_KEY', b'MY MESSAGE'])