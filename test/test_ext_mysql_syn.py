import unittest
import unittest.mock

"""
Before running this test:
Use a special MySql instance at localhost (for testing purposes only).
Create user for tests:
mysql> CREATE USER 'fairways'@'localhost' IDENTIFIED BY 'fairways';
mysql> GRANT ALL PRIVILEGES ON * . * TO 'fairways'@'localhost';
mysql> FLUSH PRIVILEGES;

"""

def setUpModule():
    pass

def tearDownModule():
    pass

class MySqlTestCase(unittest.TestCase):
    db_conn_str = "mysql://fairways:fairways@localhost:3306/"

    # @classmethod
    # def clean_test_db(cls):
    #     # import os
    #     # if os.path.exists(cls.db_test_file):
    #     #     os.remove(cls.db_test_file)


    @classmethod
    def setUpClass(cls):
        from fairways.ci import helpers
        cls.helpers = helpers

        from fairways.io.syn import mysql

        import time
        import re
        import os
        cls.mysql = mysql
        cls.time = time
        cls.re = re

        # cls.clean_test_db()
        root = helpers.getLogger()

    @classmethod
    def tearDownClass(cls):
        # cls.clean_test_db()
        pass

    def test_select_const(self):
        """
        """
        mysql = self.mysql

        # default=self.db_conn_str
        db_alias = "TEST_MYSQL"

        with unittest.mock.patch.dict('os.environ', {db_alias: self.db_conn_str}, clear=True):
            db = mysql.MySql(db_alias)

            sql = "select 99"
            result = db.fetch(sql)

        self.assertEqual(result, [{'99': 99}])

    def test_create_read(self):
        """
        """
        mysql = self.mysql

        db_alias = "TEST_MYSQL"

        with unittest.mock.patch.dict('os.environ', {db_alias: self.db_conn_str}, clear=True):
            db = mysql.MySql(db_alias)

            sql = """DROP DATABASE IF EXISTS fairways;"""

            db.execute(sql)

            sql = """CREATE DATABASE fairways;"""

            db.execute(sql)

            sql = """CREATE TABLE fairways.fairways (id INT, name TEXT, PRIMARY KEY (id));"""
            
            db.execute(sql)

            sql = """insert into fairways.fairways (id, name) values (1, "My Way");"""
            
            db.execute(sql)

            sql = """select name from fairways.fairways where id=1;"""
            
            result = db.fetch(sql)

            sql = """DROP DATABASE IF EXISTS fairways;"""

            db.execute(sql)

        self.assertEqual(result, [{'name': 'My Way'}])


