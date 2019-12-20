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
        from fairways.io.syn import amqp
        import time
        import re
        import os
        cls.time = time
        cls.re = re

        cls.amqp = amqp
        cls.net = (AmqpConsumeQuery, AmqpPublishQuery, AmqpExchangeTemplate, AmqpQueueTemplate)

        # cls.clean_test_db()

        root = helpers.getLogger()
        import logging
        root.setLevel(logging.WARN)

    @classmethod
    def tearDownClass(cls):
        # cls.clean_test_db()
        pass

    def test_text(self):
        """
        """

        (AmqpConsumeQuery, AmqpPublishQuery, AmqpExchangeTemplate, AmqpQueueTemplate) = self.net
        AmqpDriver = self.amqp.AmqpDriver

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

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].body, b'MY MESSAGE')

    def test_json(self):
        """
        """

        (AmqpConsumeQuery, AmqpPublishQuery, AmqpExchangeTemplate, AmqpQueueTemplate) = self.net
        AmqpDriver = self.amqp.AmqpDriver

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

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].body, b'{"mydata": "MY MESSAGE"}')

    def test_amqp_decorator(self):
        """
        """

        (AmqpConsumeQuery, AmqpPublishQuery, AmqpExchangeTemplate, AmqpQueueTemplate) = self.net
        AmqpDriver = self.amqp.AmqpDriver

        # AmqpPublisher = self.amqp_pub.AmqpPublisher

        # default=":memory:"
        db_alias = __name__

        test_message = "MY MESSAGE"

        with unittest.mock.patch.dict('os.environ', {db_alias: self.conn_str}, clear=True):

            # pub_options = dict(
            #     exchange="fairways",
            # )

            driver = AmqpDriver(db_alias)
            for i in range(1,5):
                driver.execute(None, message=test_message, routing_key="", options=AmqpExchangeTemplate(exchange_name='fairways-1'))
            for i in range(1,5):
                driver.execute(None, message=test_message, routing_key="", options=AmqpExchangeTemplate(exchange_name='fairways-2'))

            # driver.close()

            # options = dict(
            #     queue="fairways",
            #     kwargs=dict(timeout=10,encoding='utf-8')
            # )
            # consumer = AmqpConsumer(options, db_alias, AmqpDriver, {})

            # driver = AmqpDriver(db_alias)

            @self.amqp.entrypoint(queue="fairways-1")
            def run_it(message):
                print("LOOP 1 ==========================================>\n", message)

            @self.amqp.entrypoint(queue="fairways-2")
            def run_it(message):
                print("LOOP 2 ==========================================>\n", message)

            print("################# DECORATOR LOOP")
            self.amqp.entrypoint.run(args=["--amqp", db_alias])
            # driver.on_message(run_it, queue="fairways")

            # result = self.helpers.run_asyn(consumer.get_records())

        # self.assertEqual(len(result), 1)
        # self.assertEqual(result[0].body, b'MY MESSAGE')
