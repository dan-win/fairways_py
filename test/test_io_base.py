import unittest
import unittest.mock

def setUpModule():
    pass

def tearDownModule():
    pass



class MockDriver:
    MAX_CONN = 5

    LAST_ID = 0

    @classmethod
    def reset(cls):
        cls.LAST_ID = 0

    def __init__(self, env_varname):
        self.__class__.LAST_ID = self.__class__.LAST_ID + 1
        self.id = self.__class__.LAST_ID
        self.env_varname = env_varname
    
    def __str__(self):
        return f'Connection {self.id}'


class ConnectionPoolTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from fairways.ci import helpers
        cls.helpers = helpers

        from fairways.io.generic import base 
        cls.base = base

        import re
        import os, sys

        cls.re = re
        cls.os = os
        
        root = helpers.getLogger()

    @classmethod
    def tearDownClass(cls):
        MockDriver.reset()

    def tearDown(self):
        MockDriver.reset()

    def test_pool_not_filled(self):
        """
        """
        ConnectionPool = self.base.ConnectionPool
        env_varname = "env_conn_str"

        # # @decorators.asyncmethod.io_task
        # async def test(ctx, dba=None):
        #     await dba.CREATE_TABLE.execute()
        #     await dba.INSERT_DATA.execute()
        #     result = await dba.SELECT_DATA.get_records()
        #     return result
    
        # with unittest.mock.patch.dict('os.environ', {db_alias: self.db_test_file}, clear=True):
        #     # result = test(ctx)
        # result = self.helpers.run_asyn(AsyncLoop.run())

        trace = []

        for i in range(1, MockDriver.MAX_CONN + 2):
            conn = ConnectionPool.select(MockDriver, env_varname)
            trace.append(str(conn))

        pool = ConnectionPool._pool.get(env_varname)
        self.assertEqual(len(pool.connections), MockDriver.MAX_CONN)

        self.assertListEqual(trace, [
            'Connection 1',
            'Connection 2',
            'Connection 3',
            'Connection 4',
            'Connection 5',
            'Connection 1'
        ])

