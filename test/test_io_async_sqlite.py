import unittest

def setUpModule():
    pass

def tearDownModule():
    pass


class SqLiteTestCase(unittest.TestCase):
    db_test_file = "./test.sqlite"

    @classmethod
    def clean_test_db(cls):
        import os
        if os.path.exists(cls.db_test_file):
            os.remove(cls.db_test_file)

    @classmethod
    def setUpClass(cls):
        import asyncio
        from fairways.io.asyn import sqlite
        import time
        import concurrent.futures
        import re
        import os
        cls.asyncio = asyncio
        cls.sqlite = sqlite
        cls.time = time
        cls.futures = concurrent.futures
        cls.re = re
        cls.clean_test_db()

    @classmethod
    def tearDownClass(cls):
        cls.clean_test_db()

    def test_select_const(self):
        """
        """
        sqlite = self.sqlite
        asyncio = self.asyncio

        db = sqlite.SqLite(default=":memory:")

        sql = "select 99"
        result = run_asyn(db.fetch(sql))

        self.assertEqual(result, [{'99': 99}])

    def test_create_read(self):
        """
        """
        sqlite = self.sqlite
        asyncio = self.asyncio

        db = sqlite.SqLite(default=self.db_test_file)

        sql = """CREATE TABLE fairways (
                id integer primary key,
                name varchar
            );"""
        result = run_asyn(db.execute(sql))

        sql = """insert into fairways (id, name) values (1, "My Way");"""
        result = run_asyn(db.execute(sql))

        sql = """select name from fairways where id=1;"""
        result = run_asyn(db.fetch(sql))

        self.assertEqual(result, [{'name': 'My Way'}])


def run_asyn(coro_obj):
    import asyncio
    loop = asyncio.get_event_loop()
    task = asyncio.ensure_future(coro_obj, loop=loop)
    # Note that "gather" wraps results into list:
    (result,) = loop.run_until_complete(asyncio.gather(task))
    return result
