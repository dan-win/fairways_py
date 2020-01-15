import unittest
import unittest.mock

def setUpModule():
    pass

def tearDownModule():
    pass

class AsyncLoopTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from fairways.ci import helpers
        cls.helpers = helpers
        # cls.run_asyn = helpers.run_asyn

        from fairways.io.asyn import base 
        cls.base = base

        import asyncio
        import concurrent.futures
        import re
        import os, sys

        # cls.decorators = decorators
        cls.asyncio = asyncio
        cls.futures = concurrent.futures
        cls.re = re
        cls.os = os
        
        root = helpers.getLogger()

    @classmethod
    def tearDownClass(cls):
        pass

    def test_loop_simple_run(self):
        """
        """
        AsyncLoop = self.base.AsyncLoop
        asyncio = self.asyncio
        # decorators = self.decorators

        # # @decorators.asyncmethod.io_task
        # async def test(ctx, dba=None):
        #     await dba.CREATE_TABLE.execute()
        #     await dba.INSERT_DATA.execute()
        #     result = await dba.SELECT_DATA.get_records()
        #     return result
    
        # with unittest.mock.patch.dict('os.environ', {db_alias: self.db_test_file}, clear=True):
        #     # result = test(ctx)
        # result = self.helpers.run_asyn(AsyncLoop.run())
        loop = asyncio.get_event_loop()
        tasks = asyncio.gather(*[
            AsyncLoop().run(loop),
            AsyncLoop().run(loop)
        ], loop=loop)
        loop.run_until_complete(tasks)
        # loop.close()
        # self.assertEqual(result, [{'name': 'My Way'}])


