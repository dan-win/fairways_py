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
        cls.run_asyn = helpers.run_asyn

        from fairways.io.asyn import sqlite
        from fairways.io.generic import dbi
        from fairways.decorators import asyncmethod

        import asyncio
        import concurrent.futures
        import re
        import os, sys
        cls.dbi = dbi
        cls.asyncmethod = asyncmethod
        cls.asyncio = asyncio
        cls.futures = concurrent.futures
        cls.sqlite = sqlite
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
        dbi = self.dbi
        sqlite = self.sqlite
        asyncio = self.asyncio
        asyncmethod = self.asyncmethod
        Driver = sqlite.SqLite

        manager = dbi.DbTaskSetManager()
        db_alias = "TEST_SQLITE"

        @manager.set_dba
        class TestTaskSet(dbi.DbTaskSet):

            CREATE_TABLE = dbi.Query(
                """CREATE TABLE fairways (
                    id integer primary key,
                    name varchar
                );""", 
                db_alias, 
                Driver,
                ()
            )

            INSERT_DATA = dbi.Query(
                """insert into fairways (id, name) values (1, "My Way");""", 
                db_alias, 
                Driver,
                ()
            )

            SELECT_DATA = dbi.Query(
                """select name from fairways where id=1;""", 
                db_alias, 
                Driver,
                ()
            )

        ctx = {}

        @asyncmethod.io_task
        @manager.inject_dba_decorator(manager)
        async def test(ctx, dba=None):
            await dba.CREATE_TABLE.execute()
            await dba.INSERT_DATA.execute()
            result = await dba.SELECT_DATA.get_records()
            return result
    
        with unittest.mock.patch.dict('os.environ', {db_alias: self.db_test_file}, clear=True):
            result = test(ctx)

        self.assertEqual(result, [{'name': 'My Way'}])


