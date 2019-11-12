import unittest
import unittest.mock

def setUpModule():
    pass

def tearDownModule():
    pass

from test.test_env import SKIP_EXT_DB_SERVERS
@unittest.skipIf(SKIP_EXT_DB_SERVERS, 
    "Skip when test servers are not available in environment")
class SynAmqpPublishConsumeTestCase(unittest.TestCase):
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

        from fairways.io.generic.net import (AmqpConsumeQuery, AmqpPublishQuery, AmqpExchangeTemplate, AmqpQueueTemplate)
        from fairways.io.syn.amqp import AmqpDriver
        import time
        import re
        import os
        cls.time = time
        cls.re = re

        cls.amqp = (AmqpConsumeQuery, AmqpPublishQuery, AmqpExchangeTemplate, AmqpQueueTemplate, AmqpDriver)

        # cls.clean_test_db()

        root = helpers.getLogger()

    @classmethod
    def tearDownClass(cls):
        # cls.clean_test_db()
        pass

    def test_text(self):
        """
        """

        (AmqpConsumeQuery, AmqpPublishQuery, AmqpExchangeTemplate, AmqpQueueTemplate, AmqpDriver) = self.amqp

        # default=":memory:"
        db_alias = __name__

        test_message = "MY MESSAGE"

        with unittest.mock.patch.dict('os.environ', {db_alias: self.conn_str}, clear=True):

            pub_options = AmqpExchangeTemplate(
                exchange_name="fairways",
            )

            test_publisher = AmqpPublishQuery(pub_options, db_alias, AmqpDriver, {})
            test_publisher.execute(message=test_message)

            options = AmqpQueueTemplate(
                queue_name="fairways",
                # kwargs=dict(timeout=10,encoding='utf-8')
            )
            consumer = AmqpConsumeQuery(options, db_alias, AmqpDriver, {})

            result = consumer.get_records()

        self.assertEqual(result.body, b'MY MESSAGE')

    def test_json(self):
        """
        """

        (AmqpConsumeQuery, AmqpPublishQuery, AmqpExchangeTemplate, AmqpQueueTemplate, AmqpDriver) = self.amqp

        # default=":memory:"
        db_alias = __name__

        test_message = {"mydata":"MY MESSAGE"}

        with unittest.mock.patch.dict('os.environ', {db_alias: self.conn_str}, clear=True):

            pub_options = AmqpExchangeTemplate(
                exchange_name="fairways",
                content_type="application/json"
            )

            test_publisher = AmqpPublishQuery(pub_options, db_alias, AmqpDriver, {})
            test_publisher.execute(message=test_message)

            options = AmqpQueueTemplate(
                queue_name="fairways",
                # kwargs=dict(timeout=10,encoding='utf-8')
            )
            consumer = AmqpConsumeQuery(options, db_alias, AmqpDriver, {})

            result = consumer.get_records()

        self.assertDictEqual(result.body, b'{"mydata": "MY MESSAGE"}')