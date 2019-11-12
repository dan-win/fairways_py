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
        from fairways.io import generic as io_generic 
        from fairways import decorators
        cls.io_generic = io_generic

        cls.decorators = decorators
        import unittest.mock

    @classmethod
    def tearDownClass(cls):
        pass
    

    def setUp(self):
        self.decorators.connection.define.reset_registry()

    def test_create(self):
        """
        """
        QueriesSet = self.io_generic.QueriesSet
        SqlQuery = self.io_generic.SqlQuery
        decorators = self.decorators

        @decorators.connection.define()
        class TestDb(QueriesSet):
            QUERY1 = SqlQuery(
                "select * from t1",
                "DB_CONN",
                lambda x: x
            )

        @decorators.use.connection('dba')
        def test(ctx, dba=None, unused_arg=None):
            return dba

        db = test(None)

        attrs = [name for name in dir(db) if not name.startswith('_')]
        self.assertTrue(isinstance(db.QUERY1, SqlQuery))

    def test_create_fixture(self):
        """
        """
        QueriesSet = self.io_generic.QueriesSet
        SqlQuery = self.io_generic.SqlQuery
        FixtureQuery = self.io_generic.FixtureQuery
        decorators = self.decorators

        @decorators.connection.define()
        class TestDb(QueriesSet):
            QUERY1 = SqlQuery(
                "select * from t1",
                "DB_CONN",
                lambda x: x
            )

        class MyLocalFixture(QueriesSet):
            QUERY1 = FixtureQuery(
                [{"name": "fixture value"}]
            )

        @decorators.use.connection("dba")
        def test(ctx, dba=None, unused_arg=None):
            return dba

        result = test(None)

        self.assertEqual(result.__name__, 'TestDb', 
            "Current DbTaskSetManager should be same as used for last 'use_db' invocation")

        module_conn = decorators.connection.define.find_module_entity(__name__)
        with unittest.mock.patch.object(module_conn, "subject", MyLocalFixture):
            fixture = test(None)

        print("Test stringify behaviour: %s" % fixture)

        result = fixture.QUERY1.get_records()
        self.assertEqual(len(result), 1)
        self.assertDictEqual(result[0], {'name': 'fixture value'})

        self.assertEqual(fixture.__name__, 'MyLocalFixture')

        self.assertEqual(test(None).__name__, 'TestDb', 
            "Current QueriesSet should be same as used for last 'set_module_db_taskset' invocation")



