import os, re, pickle, json, logging, redis, pymysql
from sqlalchemy import create_engine

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
    with open(fpath, 'wb') as f:
        f.write(json.dumps(data, ensure_ascii=False, default=json_serial).encode('utf8'))

def loadjson(fpath):
    with open(fpath, 'rb') as f:
        s = f.read()
        return json.loads(s.decode('utf-8'))

def json_stream(fpath):
    def wrapper(data):
        with open(fpath, 'wb') as f:
            f.write(json.dumps(data, ensure_ascii=False, default=json_serial).encode('utf8'))
    return wrapper

def dumpxhtml(fpath, data):
    with open(fpath, 'wb') as f:
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
        with open(fpath, 'wb') as f:
            f.write(json.dumps(data, ensure_ascii=False, default=json_serial).encode('utf8'))

    def _readdata(self, fpath):
        with open(fpath, 'rb') as f:
            s = f.read()
        return json.loads(s.decode('utf-8'))

    def snapshot(self, fname):
        """
        Chainable wrapper for underscore "closure":)
        """
        fpath = self._fmt_path(datakey)
        def wrapper(data):
            with open(fpath, 'wb') as f:
                f.write(json.dumps(data, ensure_ascii=False).encode('utf8'))
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
        log.debug("Pool connections: {}".format(cls._pool))
        return connection


class Redis:
    def __init__(self, env_varname='REDIS_ADDRESS', default='localhost:6379'):
        redis_host, redis_port = os.getenv(env_varname, default).split(":")
        self.engine = redis.StrictRedis(host=redis_host, port=int(redis_port), db=0)


class MySql:

    def __init__(self, env_varname='DB_CONN', default='localhost:3306'):
        conn_str = os.getenv(env_varname, default)

        user, password, host, port, database = re.match('mysql://(.*?):(.*?)@(.*?):(.*?)/(.*)', conn_str).groups()
        self.engine = pymysql.connect(host=host,
                                 user=user,
                                 password=password,                             
                                 db=database,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
        # print()
    
    def get_records(self,sql):
        with self.engine.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()


class Alchemy:
    def __init__(self, env_varname='DB_CONN', default=None):
        conn_str = os.getenv(env_varname, default)
        self.engine = create_engine(conn_str)
        # user, password, host, database = re.match('mysql://(.*?):(.*?)@(.*?)/(.*)', url).groups()
        # print()
    
    def get_records(self, sql):
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