import unittest
import unittest.mock

def setUpModule():
    pass

def tearDownModule():
    pass


from test.test_env import SKIP_EXT_DB_SERVERS
@unittest.skipIf(SKIP_EXT_DB_SERVERS, 
    "Skip when test servers are not available in environment")
class AsynAmqpPublishConsumeTestCase(unittest.TestCase):
    conn_str = "amqp://fairways:fairways@localhost:5672/%2f"

    # @classmethod
    # def clean_test_db(cls):
    #     import os
    #     if os.path.exists(cls.conn_str):
    #         os.remove(cls.conn_str)

    @classmethod
    def setUpClass(cls):
        from fairways.ci import helpers
        cls.helpers = helpers

        from fairways.io.asyn.consumer import amqp

        from fairways.io.asyn.publisher import amqp as amqp_pub

        import asyncio
        import time
        import concurrent.futures
        import re
        import os
        cls.asyncio = asyncio
        cls.time = time
        cls.futures = concurrent.futures
        cls.re = re

        cls.amqp = amqp

        cls.amqp_pub = amqp_pub

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

        AmqpConsumer = self.amqp.AmqpConsumer
        AmqpDriver = self.amqp.AmqpDriver

        AmqpPublisher = self.amqp_pub.AmqpPublisher

        # default=":memory:"
        db_alias = __name__

        test_message = "MY MESSAGE"

        with unittest.mock.patch.dict('os.environ', {db_alias: self.conn_str}, clear=True):

            pub_options = dict(
                exchange="fairways",
            )

            test_publisher = AmqpPublisher(pub_options, db_alias, AmqpDriver, {})
            self.helpers.run_asyn(test_publisher.execute(message=test_message))

            options = dict(
                queue="fairways",
                kwargs=dict(timeout=10,encoding='utf-8')
            )
            consumer = AmqpConsumer(options, db_alias, AmqpDriver, {})

            result = self.helpers.run_asyn(consumer.get_records())

        self.assertEqual(result.body, b'MY MESSAGE')

