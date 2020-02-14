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
# granst select on <testtabsle> to houston;


from test.test_env import SKIP_EXT_DB_SERVERS
@unittest.skipIf(SKIP_EXT_DB_SERVERS, 
    "Skip when test servers are not available in environment")
class CassandraDbTestCase(unittest.TestCase):
    CONN_STR = "cassandra://localhost:9043?request_timeout=30.0"

    @classmethod
    def clean_test_db(cls):
        pass

    @classmethod
    def setUpClass(cls):
        from fairways.ci import helpers
        import asyncio
        from fairways.io.asyn import cassandra
        import time
        import re
        import os

        cls.helpers = helpers
        cls.asyncio = asyncio
        cls.cassandra = cassandra
        cls.time = time
        cls.re = re

        cls.clean_test_db()
        root = helpers.getLogger()

    @classmethod
    def tearDownClass(cls):
        cls.clean_test_db()

    def test_create_read(self):
        """
        """
        cassandra = self.cassandra

        db_alias = "MY_TEST_CASSANDRA"

        with unittest.mock.patch.dict('os.environ', {db_alias: self.CONN_STR}, clear=True):
            db = cassandra.Cassandra(db_alias)

            cql = """CREATE keyspace if not exists test_keyspace with replication = {{'class': 'SimpleStrategy', 'replication_factor':3}};"""
            
            res = self.helpers.run_asyn(db.execute(cql))
            print("--->", res)

            cql = """use test_keyspace;"""
            
            res = self.helpers.run_asyn(db.execute(cql))
            print("--->", res)

            cql = """CREATE TABLE if not exists test_keyspace.fairways (id int primary key, name varchar);"""
            
            res = self.helpers.run_asyn(db.execute(cql))
            print("--->", res)

            cql = """insert into test_keyspace.fairways (id, name) values (1, 'My Way');"""
            
            res = self.helpers.run_asyn(db.execute(cql))
            print("--->", res)

            cql = """select name from test_keyspace.fairways where id=1;"""
            
            result = self.helpers.run_asyn(db.fetch(cql))
            print("--->", result)

            cql = """DROP keyspace if exists test_keyspace;"""
            
            # self.helpers.run_asyn(db.execute(cql))


        self.assertEqual(len(result), 1)
        self.assertDictEqual(result[0], {'name': 'My Way'})

