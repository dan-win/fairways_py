import unittest
import unittest.mock

def setUpModule():
    pass

def tearDownModule():
    pass

class DbiTasksTestCase(unittest.TestCase):
    db_test_file = "./test_dbi.sqlite"

    @classmethod
    def clean_test_db(cls):
        import os
        if os.path.exists(cls.db_test_file):
            os.remove(cls.db_test_file)

    @classmethod
    def setUpClass(cls):
        from fairways.ci import helpers
        cls.helpers = helpers
        # cls.run_asyn = helpers.run_asyn

        from fairways.io import generic as io_generic 
        from fairways import decorators
        cls.io_generic = io_generic

        from fairways.io.asyn import sqlite as async_sqlite

        import asyncio
        import concurrent.futures
        import re
        import os, sys

        cls.decorators = decorators
        cls.asyncio = asyncio
        cls.futures = concurrent.futures
        cls.async_sqlite = async_sqlite
        cls.re = re
        cls.os = os
        
        cls.clean_test_db()
        root = helpers.getLogger()

    @classmethod
    def tearDownClass(cls):
        cls.clean_test_db()

    def test_dba(self):
        """
        """
        QueriesSet = self.io_generic.QueriesSet
        SqlQuery = self.io_generic.SqlQuery
        async_sqlite = self.async_sqlite
        asyncio = self.asyncio
        decorators = self.decorators

        db_alias = "TEST_SQLITE_ASYN"

        @decorators.connection.define()
        class TestTaskSet(QueriesSet):

            CREATE_TABLE = SqlQuery(
                """CREATE TABLE fairways (
                    id integer primary key,
                    name varchar
                );""", 
                db_alias, 
                async_sqlite.SqLite,
                ()
            )

            INSERT_DATA = SqlQuery(
                """insert into fairways (id, name) values (1, "My Way");""", 
                db_alias, 
                async_sqlite.SqLite,
                ()
            )

            SELECT_DATA = SqlQuery(
                """select name from fairways where id=1;""", 
                db_alias, 
                async_sqlite.SqLite,
                ()
            )

        ctx = {}

        # @decorators.asyncmethod.io_task
        @decorators.use.connection("dba")
        async def test(ctx, dba=None):
            await dba.CREATE_TABLE.execute()
            await dba.INSERT_DATA.execute()
            result = await dba.SELECT_DATA.get_records()
            return result
    
        with unittest.mock.patch.dict('os.environ', {db_alias: self.db_test_file}, clear=True):
            # result = test(ctx)
            result = self.helpers.run_asyn(test(ctx))

        self.assertEqual(result, [{'name': 'My Way'}])


