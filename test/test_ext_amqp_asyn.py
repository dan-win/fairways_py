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
        from fairways.io.asyn import base

        from fairways.io.asyn import amqp
        from fairways.io.asyn.consumer import amqp as amqp_sub

        from fairways.io.asyn.publisher import amqp as amqp_pub
        from fairways.decorators import entrypoint
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
        cls.amqp_sub = amqp_sub
        cls.amqp_pub = amqp_pub

        cls.entrypoint = entrypoint
        cls.base = base

        # cls.clean_test_db()

        root = helpers.getLogger()

    @classmethod
    def tearDownClass(cls):
        # cls.clean_test_db()
        pass

    @unittest.skip("")
    def test_consume(self):
        """
        """
        asyncio = self.asyncio

        AmqpConsumer = self.amqp_sub.AmqpConsumer
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
            # for i in range(1,10): 
            self.helpers.run_asyn(test_publisher.execute(message=test_message))

            options = dict(
                queue="fairways",
                kwargs=dict(timeout=10,encoding='utf-8')
            )
            consumer = AmqpConsumer(options, db_alias, AmqpDriver, {})

            result = self.helpers.run_asyn(consumer.get_records())

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].body, b'MY MESSAGE')

    @unittest.skip("")
    def test_consume_forewer(self):
        """
        """
        asyncio = self.asyncio

        AmqpConsumer = self.amqp_sub.AmqpConsumer
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
            # for i in range(1,10): 
            self.helpers.run_asyn(test_publisher.execute(message=test_message))

            options = dict(
                queue="fairways",
                kwargs=dict(timeout=10,encoding='utf-8')
            )
            # consumer = AmqpConsumer(options, db_alias, AmqpDriver, {})

            driver = AmqpDriver(db_alias)

            async def run_it(message):
                print(message)

            driver.consume(run_it, queue="fairways")

            # result = self.helpers.run_asyn(consumer.get_records())

        # self.assertEqual(len(result), 1)
        # self.assertEqual(result[0].body, b'MY MESSAGE')

    @unittest.skip("")
    def test_amqp_consumer_decorator(self):
        """
        """
        asyncio = self.asyncio

        AmqpConsumer = self.amqp_sub.AmqpConsumer
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
            for i in range(1,5):
                self.helpers.run_asyn(test_publisher.execute(message=test_message))

            # options = dict(
            #     queue="fairways",
            #     kwargs=dict(timeout=10,encoding='utf-8')
            # )
            # consumer = AmqpConsumer(options, db_alias, AmqpDriver, {})

            driver = AmqpDriver(db_alias)

            @self.amqp.consumer(queue="fairways")
            def run_it(message):
                # print("LOOP\n", message)
                print("Consumer: got message %s\n" % message)

            print("################# DECORATOR LOOP")
            self.amqp.consumer.run(args=["--amqp", db_alias])
            # driver.on_message(run_it, queue="fairways")

            # result = self.helpers.run_asyn(consumer.get_records())

        # self.assertEqual(len(result), 1)
        # self.assertEqual(result[0].body, b'MY MESSAGE')

    # @unittest.skip("")
    def test_amqp_producer_decorator(self):
        """
        """
        asyncio = self.asyncio

        AmqpConsumer = self.amqp_sub.AmqpConsumer
        AmqpDriver = self.amqp.AmqpDriver

        AmqpPublisher = self.amqp_pub.AmqpPublisher

        # default=":memory:"
        db_alias = __name__

        test_message = "MY MESSAGE"

        with unittest.mock.patch.dict('os.environ', {db_alias: self.conn_str}, clear=True):

            pub_options = dict(
                exchange="fairways",
            )


            @self.amqp.producer(exchange="fairways")
            def publish():
                print("calling publish()...")
                return "MY_MESSAGE"

            # test_publisher = AmqpPublisher(pub_options, db_alias, AmqpDriver, {})
            # for i in range(1,5):
            #     self.helpers.run_asyn(test_publisher.execute(message=test_message))

            # options = dict(
            #     queue="fairways",
            #     kwargs=dict(timeout=10,encoding='utf-8')
            # )
            # consumer = AmqpConsumer(options, db_alias, AmqpDriver, {})

            driver = AmqpDriver(db_alias)

            @self.amqp.consumer(queue="fairways")
            def run_it(message):
                print("Received:============================>", message)
                # print("LOOP\n")
            
            async def runner():
                for i in range(1,5):
                    publish()
                    await asyncio.sleep(0.1)

            print("################# DECORATOR LOOP")
            consumers_future = self.amqp.consumer.create_tasks_future(args=["--amqp", db_alias])
            producers_future = self.amqp.producer.create_tasks_future(args=["--amqp", db_alias])
            tasks = asyncio.gather(*[producers_future, consumers_future, runner()])
            async def destructor():
                print("Closing driver...")
                await driver.close()
            result = self.base.run_asyn(tasks, destructor)

            # driver.on_message(run_it, queue="fairways")

            # result = self.helpers.run_asyn(consumer.get_records())

        # self.assertEqual(len(result), 1)
        # self.assertEqual(result[0].body, b'MY MESSAGE')
