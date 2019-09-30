import unittest
from fairways.ci.templates.fixture_template import FixtureTestTemplate


class FixtureTemplateTestCase(FixtureTestTemplate):
    subject_module = __name__
    # fixture = {}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fixture = {
            "QUERY1": [{"name": "fixture_value"}]
        }

        from fairways.io import generic as io_generic 
        from fairways import decorators
        from fairways.decorators import entities
        cls.io_generic = io_generic
        cls.decorators = decorators
        cls.entities = entities

        import unittest.mock


    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.decorators.connection.define.reset_registry()

    def test_with_fixture(self):
        "Override inherited to prevent dry run before test method is defined"
        pass

    def test_create(self):
        """
        """
        QueriesSet = self.io_generic.QueriesSet
        SqlQuery = self.io_generic.SqlQuery
        decorators = self.decorators

        registry = self.entities.Mark._registry

        @decorators.connection.define()
        class TestDb(QueriesSet):
            QUERY1 = SqlQuery(
                "select * from t1",
                "DB_CONN",
                lambda x: x
            )

        @decorators.use.connection('dba')
        def some_task(ctx, dba=None, unused_arg=None):
            return dba

        @decorators.entrypoint.qa()
        def runner(ctx):
            return some_task(ctx)
        
        print(f"\n*******************\nEntities registry: {len(registry)}; {registry}\n\n")


        # module_conn = decorators.connection.define.find_module_entity(__name__)
        # with unittest.mock.patch.object(module_conn, "subject", MyLocalFixture):
        #     fixture = test(None)

        result = self.get_response_with_fixture()
        self.assertEqual(result, "")
        # self.assertEqual(fixture.QUERY1.get_records(), [{'name': 'fixture value'}])
        # self.assertEqual(fixture.__name__, 'MyLocalFixture')

        # self.assertEqual(test(None).__name__, 'TestDb', 
        #     "Current QueriesSet should be same as used for last 'set_module_db_taskset' invocation")



