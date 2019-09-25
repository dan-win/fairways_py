import unittest


import json
import os

def setUpModule():
    pass

def tearDownModule():
    pass


class DbiTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from fairways.io.generic.dbi import (DbTaskSetManager, DbTaskSet, Query, FixtureQuery)
        cls.DbTaskSetManager = DbTaskSetManager
        cls.DbTaskSet = DbTaskSet
        cls.Query = Query
        cls.FixtureQuery = FixtureQuery

    @classmethod
    def tearDownClass(cls):
        pass

    def test_create(self):
        """
        """
        DbTaskSetManager = self.DbTaskSetManager
        DbTaskSet = self.DbTaskSet
        Query = self.Query

        manager = DbTaskSetManager()

        @manager.set_dba
        class TestDb(DbTaskSet):
            QUERY1 = Query(
                "select * from t1",
                "DB_CONN",
                lambda x: x
            )

        @DbTaskSetManager.inject_dba_decorator(manager)
        def test(ctx, dba=None, unused_arg=None):
            return dba

        db = test(None)

        attrs = [name for name in dir(db) if not name.startswith('_')]
        # self.assertEqual(attrs, ['queries'])
        self.assertTrue(isinstance(db.QUERY1, Query))

    def test_create_fixture(self):
        """
        """
        DbTaskSetManager = self.DbTaskSetManager
        DbTaskSet = self.DbTaskSet
        Query = self.Query
        FixtureQuery = self.FixtureQuery

        manager = DbTaskSetManager()

        @manager.set_dba
        class TestDb(DbTaskSet):
            QUERY1 = Query(
                "select * from t1",
                "DB_CONN",
                lambda x: x
            )

        @DbTaskSetManager.inject_dba_decorator(manager)
        def test(ctx, dba=None, unused_arg=None):
            return dba

        self.assertEqual(test(None).__name__, 'TestDb', 
            "Current DbTaskSetManager should be same as used for last 'use_db' invocation")

        manager.add_fixture("MyLocalFixture",
            QUERY1 = [{"name": "value"}]
        )

        saved = manager.select_profile("MyLocalFixture")

        fixture = test(None)

        print("Test stringify behaviour: %s" % fixture)

        self.assertEqual(fixture.QUERY1.get_records(), [{'name': 'value'}])
        self.assertEqual(test(None).__name__, 'MyLocalFixture')

        manager.select_profile(saved)

        self.assertEqual(test(None).__name__, 'TestDb', 
            "Current DbTaskSet should be same as used for last 'set_module_db_taskset' invocation")

    def test_create_fixture_context(self):
        """
        """
        DbTaskSetManager = self.DbTaskSetManager
        DbTaskSet = self.DbTaskSet
        Query = self.Query
        FixtureQuery = self.FixtureQuery

        manager = DbTaskSetManager()

        @manager.set_dba
        class TestDb(DbTaskSet):
            QUERY1 = Query(
                "select * from t1",
                "DB_CONN",
                lambda x: x
            )

        @DbTaskSetManager.inject_dba_decorator(manager)
        def test(ctx, dba=None, unused_arg=None):
            return dba

        self.assertEqual(test(None).__name__, 'TestDb', 
            "Current DbTaskSetManager should be same as used for last 'use_db' invocation")

        manager.add_fixture("MyLocalFixture",
            QUERY1 = [{"name": "value"}]
        )
        
        with manager.another_context("MyLocalFixture"):

            fixture = test(None)

            print("Test stringify behaviour: %s" % fixture)

            self.assertEqual(fixture.QUERY1.get_records(), [{'name': 'value'}])
            self.assertEqual(test(None).__name__, 'MyLocalFixture')

        self.assertEqual(test(None).__name__, 'TestDb', 
            "Profile should be restored after exit form contexdt manager")


if __name__ == '__main__':
    unittest.main(verbosity=2)
