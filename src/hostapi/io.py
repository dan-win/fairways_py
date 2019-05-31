# -*- coding: utf-8 -*-
import os, re, pickle, json, logging, redis, pymysql
from sqlalchemy import create_engine

from .underscore import Underscore as _

TRACE_MODE = os.getenv('DEBUG_TRACE', False)

level = logging.DEBUG
if TRACE_MODE:
    level = logging.CRITICAL

logging.basicConfig(
    # filename='example.log', 
    format='%(asctime)s %(levelname)s:%(message)s', 
    level=level)
log = logging.getLogger(__name__)    

def dumpjson(fpath, data):
    with open(fpath, 'w') as f:
        f.write(json.dumps(data, ensure_ascii=False, default=json_serial))

def loadjson(fpath):
    with open(fpath, 'r') as f:
        s = f.read()
        return json.loads(s.decode('utf-8'))

def json_stream(fpath):
    def wrapper(data):
        with open(fpath, 'w') as f:
            f.write(json.dumps(data, ensure_ascii=False, default=json_serial))
    return wrapper

def dumpxhtml(fpath, data):
    with open(fpath, 'w') as f:
        f.write(data.encode('utf8'))


class DataStore:
    FILEEXT = "_"

    def __init__(self, mount_dir):
        self.mount_dir = mount_dir

    def _writedata(self, fpath, data):
        raise NotImplemented()

    def _readdata(self, fpath):
        raise NotImplemented()

    def _fmt_path(self, datakey):
        fname = '{}.{}'.format(datakey, self.FILEEXT)
        return os.path.join(self.mount_dir, fname)

    def push(self, datakey, data):
        fpath = self._fmt_path(datakey)
        self._writedata(fpath, data)

    def pull(self, datakey):
        fpath = self._fmt_path(datakey)
        return self._readdata(fpath)


class JsonStore(DataStore):
    """
    """
    FILEEXT = "json"

    def _writedata(self, fpath, data):
        with open(fpath, 'w') as f:
            f.write(json.dumps(data, ensure_ascii=False, default=json_serial))

    def _readdata(self, fpath):
        with open(fpath, 'r') as f:
            s = f.read()
        return json.loads(s)

    def snapshot(self, fname):
        """
        Chainable wrapper for underscore "closure":)
        """
        fpath = self._fmt_path(datakey)
        def wrapper(data):
            with open(fpath, 'w') as f:
                f.write(json.dumps(data, ensure_ascii=False))
        return wrapper


class XmlOut(DataStore):
    """
    Write-only facility to export XML snapshots.
    """
    FILEEXT = "xml"


class BinStore(DataStore):
    """
    Pickle
    """

    FILEEXT = "pickle"

    def _writedata(self, fpath, data):
        with open(fpath, 'wb') as f:
            pickle.dump(data, f)

    def _readdata(self, fpath):
        with open(fpath, 'rb') as f:
            data = pickle.load(f)
        return data


class NullStore(DataStore):
    """
    Empty storage as a stub
    """

    def __init__(self):
        pass

    def push(self, datakey, data):
        # print("STEP {}".format(datakey), "RESULT: ", data)
        pass

    def pull(self, datakey):
        raise NotImplemented("NullStore does not keep any data!")


class Heap:
    """
    Replacer for Airflow "xcom" which doesn't allow large data buffering.
    """

    def __init__(self, engine):
        self.engine = engine

    def push(self, datakey, data):
        self.engine.push(datakey, data)

    def pull(self, datakey):
        return self.engine.pull(datakey)


    def store(self, func):
        """
        Decorator for task callable - store result in heap
        Key === task_id
        """
        def wrapper(context):
            new_context = func(context)
            # log.debug("\nIO MESSAGE ({})\n: {}\n===\n".format(func.__name__, new_context))
            self.push(func.__name__, new_context)
            return new_context
             # Avoid xcom_push for any large data!
        return wrapper


class ConnectionPool:

    _pool = {}

    @classmethod
    def select(cls, driver_cls, env_varname):
        connection = cls._pool.get(env_varname)
        if not connection:
            connection = driver_cls(env_varname)
            cls._pool[env_varname] = connection
        # log.debug("Pool connections: {}".format(cls._pool))
        return connection

class DbDriver:
    def fetch(self, sql):
        raise NotImplemented

    def exec(self, sql):
        raise NotImplemented

    def get_records(self, query_template, **params):
        """
        Do not override
        """
        # Convert all iterables to lists to 
        query = query_template.format(**params).replace('\n', " ").replace("\"", "\'")
        log.debug("SQL: {}".format(query))
        return self.fetch(query)

    def execute(self, query_template, **params):
        """
        Do not override
        """
        query = query_template.format(**params)
        # log.debug("SQL: {}".format(query))
        return self.exec(query)


class Redis(DbDriver):
    def __init__(self, env_varname='REDIS_ADDRESS', default='localhost:6379'):
        redis_host, redis_port = os.getenv(env_varname, default).split(":")
        self.engine = redis.StrictRedis(host=redis_host, port=int(redis_port), db=0)


class MySql(DbDriver):

    @property
    def db_name(self):
        return self.conn_str.split("/")[-1]

    def _ensure_connection(self):
        if( not self.engine or not self.engine.open): 
            log.warn("Restoring DB connection: {}".format(self.db_name))
            self._connect()
    
    def _connect(self):
        user, password, host, port, database = re.match('mysql://(.*?):(.*?)@(.*?):(.*?)/(.*)', self.conn_str).groups()
        self.engine = pymysql.connect(
            host=host,
            user=user,
            password=password,                             
            db=database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True)


    def __init__(self, env_varname='DB_CONN', default='localhost:3306'):
        self.conn_str = os.getenv(env_varname, default)
        self.engine = None

        self._connect()
        # user, password, host, port, database = re.match('mysql://(.*?):(.*?)@(.*?):(.*?)/(.*)', self.conn_str).groups()
        # self.engine = pymysql.connect(host=host,
        #                          user=user,
        #                          password=password,                             
        #                          db=database,
        #                          charset='utf8mb4',
        #                          cursorclass=pymysql.cursors.DictCursor,
        #                          autocommit=True)
        # print()
    
    def fetch(self,sql):
        try:
            self._ensure_connection()
            with self.engine.cursor() as cursor:
                cursor.execute(sql)
                res = cursor.fetchall()
            return res
        except Exception as e:
            log.error("DB operation error: {} at {}".format(e, self.db_name))

    def exec(self, sql):
        try:
            self._ensure_connection()
            with self.engine.cursor() as cursor:
                res = cursor.execute(sql)
            return res
        except Exception as e:
            log.error("DB operation error: {} at {}".format(e, self.db_name))

class Alchemy(DbDriver):
    def __init__(self, env_varname='DB_CONN', default=None):
        conn_str = os.getenv(env_varname, default)
        self.engine = create_engine(conn_str)
        # user, password, host, database = re.match('mysql://(.*?):(.*?)@(.*?)/(.*)', url).groups()
        # print()
    
    def fetch(self, sql):
        with self.engine.connect() as con:
            rs = con.execute(sql)
            for row in rs:
                yield row        


# Heler to overcome json error on dates (receipt source: https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable):

from datetime import date, datetime

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

from enum import Enum

class DbTaskSet(Enum):

    def __init__(self, sql, db_env_conf, driver, meta):
        """Creates new instance of DB task 
        Note: class is based on Python Enum so
        __init__ blesses a single member of enumeration
        (See more about Python Enum class)
        
        Arguments:
            sql {str} -- Script to execute
            db_env_conf {str} -- Name of environment variable wich holds config
            driver {DbDriver} -- DbDriver subclass
            meta {dict} -- Any data to store with the task instance
        """
        # self.task_id = 'TASK_ID_DB_FETCH_' + self.name.upper()
        print("DbTaskSet - init instance", self)
        self.sql = sql
        self.db_env_conf=db_env_conf
        self.driver = driver
        self.meta = meta
    
    def get_records(self, **sql_params):

        def smart_quote(v):
            if isinstance(v, str):
                return "\"{}\"".format(v)
            return str(v)
        
        # Convert lists to comma-delimited enumeration:
        for key, value in sql_params.items():
            # Convert iterables like set to list:
            if isinstance(value, (set, map)):
                value = list(value)
            if isinstance(value, (list, tuple)):
                sql_params[key] = ",".join(_.map(value, smart_quote))

        db = ConnectionPool.select(self.driver, self.db_env_conf)
        return db.get_records(self.sql, **sql_params)

    def execute(self, **sql_params):

        def smart_quote(v):
            if isinstance(v, str):
                return "\"{}\"".format(v)
            return str(v)
            
        # Convert lists to comma-delimited enumeration:
        for key, value in sql_params.items():
            if isinstance(value, (list, tuple)):
                sql_params[key] = ",".join(_.map(value, smart_quote))

        db = ConnectionPool.select(self.driver, self.db_env_conf)
        return db.execute(self.sql, **sql_params)



    @classmethod
    def prepare_fake(cls):
        cls_name = self.__class__.__name__
        root = _fake_db_registry[cls_name]
        sorted = _.sort_by()


