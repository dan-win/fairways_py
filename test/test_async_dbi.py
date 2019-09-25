import unittest

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
        import asyncio
        from fairways.io.asyn import sqlite
        from fairways.io.sync import dbi

        from fairways.decorators import asyncmethod

        import time
        import concurrent.futures
        import re
        import os
        cls.asyncio = asyncio
        cls.sqlite = sqlite
        cls.dbi = dbi
        cls.asyncmethod = asyncmethod
        cls.time = time
        cls.futures = concurrent.futures
        cls.re = re
        cls.clean_test_db()

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
        db_alias = self.db_test_file
        Driver = sqlite.SqLite
        manager = dbi.DbTaskSetManager()

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
            try:
                await dba.CREATE_TABLE.execute()
                await dba.INSERT_DATA.execute()
                result = await dba.SELECT_DATA.get_records()
            except Exception as e:
                print(f"--->{e}")

        # result = run_asyn(test(ctx))
        result = test(ctx)

        self.assertEqual(result, [{'name': 'My Way'}])


def run_asyn(coro_obj):
    import asyncio
    loop = asyncio.get_event_loop()
    task = asyncio.ensure_future(coro_obj, loop=loop)
    # Note that "gather" wraps results into list:
    (result,) = loop.run_until_complete(asyncio.gather(task))
    return result
