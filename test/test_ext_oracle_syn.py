import unittest
import unittest.mock

def setUpModule():
    pass

def tearDownModule():
    pass

# Probably you should make some magic with you test oracle db:):
# alter session set "_ORACLE_SCRIPT"=true; 
# create user houston identified by houston;
# grant CREATE SESSION, ALTER SESSION, CREATE DATABASE LINK, CREATE MATERIALIZED VIEW, CREATE PROCEDURE, CREATE PUBLIC SYNONYM, CREATE ROLE, CREATE SEQUENCE, CREATE SYNONYM, CREATE TABLE, CREATE TRIGGER, CREATE TYPE, CREATE VIEW, UNLIMITED TABLESPACE to houston;


class OracleDbTestCase(unittest.TestCase):
    db_test_file = "./test.oracle"
    CONN_STR = "houston/houston@//localhost:51521/XE"

    @classmethod
    def clean_test_db(cls):
        pass
        # import os
        # if os.path.exists(cls.db_test_file):
        #     os.remove(cls.db_test_file)

    @classmethod
    def setUpClass(cls):
        from fairways.ci import helpers
        cls.helpers = helpers

        from fairways.io.syn import oracle

        import time
        import re
        import os
        cls.oracle = oracle
        cls.time = time
        cls.re = re

        cls.clean_test_db()
        root = helpers.getLogger()

    @classmethod
    def tearDownClass(cls):
        cls.clean_test_db()

    def test_select_const(self):
        """
        """
        oracle = self.oracle

        # default=":memory:"
        db_alias = "MY_TEST_ORACLE"

        with unittest.mock.patch.dict('os.environ', {db_alias: self.CONN_STR}, clear=True):
            db = oracle.OracleDb(db_alias)

            sql = "select 99 from dual"
            result = db.fetch(sql)

        self.assertEqual(result, [{'99': 99}])

    # def test_create_read(self):
    #     """
    #     """
    #     oracle = self.oracle

    #     db_alias = "MY_TEST_SQLITE"

    #     with unittest.mock.patch.dict('os.environ', {db_alias: self.db_test_file}, clear=True):
    #         db = oracle.SqLite(db_alias)

    #         sql = """CREATE TABLE fairways (id integer primary key, name varchar);"""
            
    #         db.execute(sql)

    #         sql = """insert into fairways (id, name) values (1, "My Way");"""
            
    #         db.execute(sql)

    #         sql = """select name from fairways where id=1;"""
            
    #         result = db.fetch(sql)
            
    #     self.assertEqual(result, [{'name': 'My Way'}])

