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

        from fairways.io import generic as io_generic 
        from fairways import decorators
        cls.io_generic = io_generic

        cls.decorators = decorators
        import unittest.mock

        from fairways.io import sync

        import re
        import os, sys

        cls.sync = sync
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
        FixtureQuery = self.io_generic.FixtureQuery
        decorators = self.decorators
        mock = self.mock

        sync = self.sync

        db_alias = "TEST_SQLITE"

        @decorators.connection.define()
        class TestTaskSet(QueriesSet):

            CREATE_TABLE = SqlQuery(
                """CREATE TABLE fairways (
                    id integer primary key,
                    name varchar
                );""", 
                db_alias, 
                sync.sqlite.SqLite,
                ()
            )

            INSERT_DATA = SqlQuery(
                """insert into fairways (id, name) values (1, "My Way");""", 
                db_alias, 
                sync.sqlite.SqLite,
                ()
            )

            SELECT_DATA = SqlQuery(
                """select name from fairways where id=1;""", 
                db_alias, 
                sync.sqlite.SqLite,
                ()
            )

        ctx = {}

        @decorators.use.connection("dba")
        async def test(ctx, dba=None):
            dba.CREATE_TABLE.execute()
            dba.INSERT_DATA.execute()
            result = dba.SELECT_DATA.get_records()
            return result
    
        with unittest.mock.patch.dict('os.environ', {db_alias: self.db_test_file}, clear=True):
            result = test(ctx)

        self.assertEqual(result, [{'name': 'My Way'}])


