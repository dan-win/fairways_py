import unittest
import unittest.mock

def setUpModule():
    pass

def tearDownModule():
    pass


from test.test_env import SKIP_EXT_DB_SERVERS
@unittest.skipIf(SKIP_EXT_DB_SERVERS, 
    "Skip when test servers are not available in environment")
class InfluxDbTestCase(unittest.TestCase):
    CONN_STR = "influxdb://houston:houston@localhost:8086/testdb"
    db_alias = "MY_TEST_INFLUX"

    @classmethod
    def setUpClass(cls):
        from fairways.ci import helpers
        cls.helpers = helpers
        
        import influxdb # Only to create/clean database

        from fairways.io.syn import influx
        from fairways.funcflow import  FuncFlow as ff

        import time
        import re
        import os
        cls.influx = influx
        cls.influxdb = influxdb
        cls.time = time
        cls.re = re
        cls.ff = ff

        root = helpers.getLogger()

    def tearDown(self):
        conn = self.influx.InfluxDBClient.from_dsn(self.CONN_STR)
        conn.query("""DROP DATABASE testdb """)

    def setUp(self):
        conn = self.influx.InfluxDBClient.from_dsn(self.CONN_STR)
        conn.query("""CREATE DATABASE testdb """)
        conn.query("""CREATE RETENTION POLICY "oneday" ON "testdb" DURATION 1d REPLICATION 1""")


    def test_create_read_insert_simple(self):
        """
        """
        influx = self.influx
        ff = self.ff

        with unittest.mock.patch.dict('os.environ', {self.db_alias: self.CONN_STR}, clear=True):
            db = influx.InfluxDb(self.db_alias)

            # line_script = """CREATE TABLE fairways (id integer primary key, name varchar);"""
            
            # db.execute(line_script)

            ####### SELECT * FROM "a_year"."downsampled_orders" LIMIT 5 
            ####### Notice that we fully qualify (that is, we use the syntax "<retention_policy>"."<measurement>") downsampled_orders in the second SELECT statement. We must specify the RP in that query to SELECT data that reside in an RP other than the DEFAULT RP

            time = self.time
            millis = int(round(time.time() * 1000))
            millis1 = millis + 1

            line_script = """INSERT  
            mymeasurement,location=us-west temperature=82 %s
            mymeasurement,location=us-west temperature=83 %s""" % (
                millis, millis1                
            )

            db.execute(line_script)

            # More about FROM syntax: https://docs.influxdata.com/influxdb/v1.7/query_language/data_exploration/#from-clause
            line_script = """SELECT * FROM mymeasurement WHERE temperature >= 70;"""
            # line_script = """SELECT * FROM testdb.oneday.mymeasurement;"""
            # line_script = """SELECT * ;"""
            
            result = db.fetch(line_script)
            result = ff.map(result, lambda record: ff.omit(record, "time"))
            print(result)
            # result = dict(result)
        
        valid_result_sample = [
            {'location': 'us-west', 'measurement': 'mymeasurement', 'temperature': 82},
            {'location': 'us-west', 'measurement': 'mymeasurement', 'temperature': 83}
        ]

        self.assertEqual(result, valid_result_sample)


    def test_create_read_insert_into(self):
        """
        """
        influx = self.influx
        ff = self.ff

        with unittest.mock.patch.dict('os.environ', {self.db_alias: self.CONN_STR}, clear=True):
            db = influx.InfluxDb(self.db_alias)

            # line_script = """CREATE TABLE fairways (id integer primary key, name varchar);"""
            
            # db.execute(line_script)

            ####### SELECT * FROM "a_year"."downsampled_orders" LIMIT 5 
            ####### Notice that we fully qualify (that is, we use the syntax "<retention_policy>"."<measurement>") downsampled_orders in the second SELECT statement. We must specify the RP in that query to SELECT data that reside in an RP other than the DEFAULT RP

            time = self.time
            millis = int(round(time.time() * 1000))
            millis1 = millis + 1

            line_script = """INSERT INTO oneday
            mymeasurement,location=us-west temperature=82 %s
            mymeasurement,location=us-west temperature=83 %s""" % (
                millis, millis1                
            )

            # line_script = """INSERT  
            # mymeasurement,location=us-west temperature=82
            # mymeasurement,location=us-west temperature=83"""

            db.execute(line_script)

            # More about FROM syntax: https://docs.influxdata.com/influxdb/v1.7/query_language/data_exploration/#from-clause

            # line_script = """SELECT * FROM mymeasurement WHERE temperature >= 70;"""
            line_script = """SELECT * FROM testdb.oneday.mymeasurement;"""
            # line_script = """SELECT * ;"""
            
            result = db.fetch(line_script)
            result = ff.map(result, lambda record: ff.omit(record, "time"))
            print(result)
            # result = dict(result)
            
        valid_result_sample = [
            {'location': 'us-west', 'measurement': 'mymeasurement', 'temperature': 82},
            {'location': 'us-west', 'measurement': 'mymeasurement', 'temperature': 83}
        ]

        self.assertDictEqual(result[0], valid_result_sample[0])
        self.assertDictEqual(result[1], valid_result_sample[1])
