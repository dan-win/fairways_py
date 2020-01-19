# -*- coding: utf-8 -*-
"""High-level entities
"""

__all__ = [
    "set_config_provider",
    "DataDriver",
    "ConnectionPool", 
    "QueriesSet", 
    "BaseQuery", 
    "ReaderMixin", 
    "WriterMixin", 
    "FixtureQuery",
    "UriConnMixin",
    "FileConnMixin",
    "UriParts"
]

import inspect
import functools
from contextlib import contextmanager
from typing import (List, Dict)
from collections import namedtuple

from collections.abc import Mapping as AbcMapping

from fairways.decorators import use

from fairways.conf import replace_env_vars

from cached_property import cached_property
from urllib.parse import parse_qs as _parse_qs

import logging
log = logging.getLogger(__name__)

import os
import sys
import re
import itertools
from abc import abstractmethod
import atexit

CONF_KEY = "CONNECTIONS"

# RE_ENV_EXPRESSION = re.compile(r"\{\$(.*?)\}")
# RE_URI_TEMPLATE = re.compile(r"(.*?)://(.*?):(.*?)@(.*?):(.*?)/(.*)")
# RE_URI_TEMPLATE = re.compile(r"(.*?)://(.*?):(.*?)@(.*?):(.*?)/(.*)")
# RE_URI_TEMPLATE = re.compile(r"(?P<scheme>.*?)://(?:(?P<user>[^:]*):(?P<password>[^@]*)@)?(?P<host>[^:^/]*)(?::(?P<port>[^/|^?]*))?(?:/(?P<path>.*))?")
RE_URI_TEMPLATE = re.compile(r"(?P<scheme>.*?)://(?:(?P<user>[^:]*):(?P<password>[^@]*)@)?(?P<host>[^:^/]*)(?::(?P<port>[^/|^?]*))?(?:/(?P<path>[^\?]*))?(?:\?(?P<params>[^?\n]+))?")
# (?P<scheme>.*?)://(?:(?P<user>[^:]*):(?P<password>[^@]*)@)?(?P<host>[^:^/]*)(?::(?P<port>[^/|^?]*))?(?:/(?P<path>[^\?]*))?(?:\?(?P<params>[^?\n]+))?

#: URI parts
UriParts = namedtuple('UriParts', 'scheme,user,password,host,port,path,params'.split(','))

# this is a pointer to the module object instance itself.
this = sys.modules[__name__]
this._config_provider = os.environ

@use.config(CONF_KEY)
def set_config_provider(config_dict):
    prev_value = this._config_provider
    if config_dict:
        this._config_provider = config_dict
    return prev_value

# def replace_env_vars(s):
#     """Replace all occurences of {$name} in string with values from os.environ
    
#     Arguments:
#         s {[str]} -- [description]
    
#     Returns:
#         [str] -- [String with replaced values]
#     """
#     def envrepl(match):
#         (env_var,) = match.groups(1)
#         return os.environ[env_var]

#     return RE_ENV_EXPRESSION.sub(envrepl, s)

def parse_conn_uri(s):
    """Split uri to parts:
    sheme, use, password, host, port, path.
    Absent parts replaced with None

    :param s: [description]
    :type s: str
    :raises ValueError: uri cannot be parsed with know pattern
    :return: Parsed uri 
    :rtype: UriParts
    """
    match = RE_URI_TEMPLATE.match(s)
    if not match:
        raise ValueError(f"Cannot parse connection string '{s}' with patterns registered")
    m = match.group
    port = m('port')
    if port is not None:
        port = int(port)
    return UriParts(m('scheme'), m('user'), m('password'), m('host'), port, m('path'), m('params'))


class UriConnMixin:
    """Mixin for Driver subclasses which could be configured with uri-like connection string"""
    def _parse_uri(self, conn_uri):
        log.debug("Parsing uri: %s", conn_uri)
        return parse_conn_uri(conn_uri)
            

class FileConnMixin:
    """Mixin for Driver subclasses which could be configured with file path (SQLite, etc...) """
    def _parse_uri(self, conn_uri):
        return UriParts(None, None, None, None, None, conn_uri, None)


class DataDriver:
    """Base class for IO driver.
    It should not be instantiated directly (instead it is a base for a real drivers).
    Implements "low-lewel" interface which manages connection directly.
    In most cases we use high-level desceendants of BaseQuery.
    
    Notes 

    - We do not implement drivers from scratch here - all subsequent drivers are facades for wide-spread packages like PyMySql, etc. But, such facades allow to use common "application protocol" for databases, HTTP resources, AMQP, etc. to make code more consistent.
    - We can define "read-only" drivers (e.g., HTTP client to fetch some data) or "write-only" drivers (e.g. logger), so it is not necessary to implement both fetch and change methods in descendants.

    :param env_varname: Name of enviromnent variable (or settings attribute) which holds connection string (e.g.: "mysql://user@pass@host/db")
    :type env_varname: str
    """

    #: Default value for connection string (e.g., it could be ":memory:" for SQLite)
    default_conn_str = ""

    #: Connection should be closed after single query (get_records or execute)
    autoclose = False

    _config_provider = os.environ

    @classmethod
    def set_config_provider(cls, config_dict):
        """Assign mapping as a config source
        
        :param config_dict: Source mapping. Default value - os.environ 
        :type config_dict: Mapping
        :return: Previous value of config provider
        :rtype: Mapping
        """
        prev_value = cls._config_provider
        cls._config_provider = config_dict
        return prev_value

    @property
    def db_name(self):
        return self.conn_str.split("/")[-1]

    @abstractmethod    
    def is_connected(self):
        """Connection status
        """
        pass
    
    def __init__(self, env_varname):
        """Constructor
        """
        # "this" points to this module here, see above
        conn_uri_raw = this._config_provider.get(env_varname, self.default_conn_str)
        conn_uri = replace_env_vars(conn_uri_raw)
        self.conn_str = conn_uri
        # Used from mixin:
        self.uri_parts = self._parse_uri(conn_uri)
        log.debug(f"Loading {self}...")
        self.engine = None

    def __str__(self):
        return f"Driver {self.__class__.__name__} | {self.conn_str}"

    @cached_property
    def qs_params(self):
        """Named parameters of query string part (after "?" char in URI)
        
        :return: Mapping
        :rtype: Mapping
        """
        def unwrap(v):
            "Unwrap all lists with single item"
            return v[0] if isinstance(v, list) and len(v) == 1 else v
        params = self.uri_parts.params
        if params:
            params = _parse_qs(params)
            return {k:unwrap(v) for k, v in params.items()}
        return {}

    @abstractmethod
    def fetch(self, backend_script):
        raise NotImplementedError("Fetch operations are not allowed for this class %s" % self.__class__.__name__)

    @abstractmethod
    def change(self, backend_script):
        raise NotImplementedError("Change operations are not allowed for this class %s" % self.__class__.__name__)

    def get_records(self, query_template, **params):
        """Read operations for data source.
        Note: This method is common for sync and async implementations (in latter case it acts as a proxy for awaitable)
        
        :param query_template: Backend-specific script to fetch data (e.g., SQL script)
        :type query_template: str
        :return: List of results
        :rtype: List[Dict[..]|NamedTuple]
        """

        # Convert all iterables to lists to 
        query = query_template.format(**params).replace('\n', " ").replace("\"", "\'")
        log.debug("SQL: %s", query)
        return self.fetch(query)

    def execute(self, query_template, **params):
        """Modify records in storage (i.e. create, update, delete).
        Note: This method is common for sync and async implementations (in latter case it acts as a proxy for awaitable)
        
        :param query_template: Backend-specific script to fetch data (e.g., SQL script)
        :type query_template: str
        :return: [description]
        :rtype: [type]
        """

        # Modify records in storage
        # This method is common for sync and async implementations (in latter case it acts as a proxy for awaitable)

        query = query_template.format(**params)
        # log.debug("SQL: %s", query)
        return self.change(query)
    
    @abstractmethod
    def close(self):
        """Close connection if alive.
        Sometimes we should re-define this method because some backends uses .close() while other .shutdown(), etc...
        """
        pass



class ConnectionPool:
    """Manage number of opened connections to resource 

    :param driver_cls: Driver class to instantiate it inside pool.
    :type driver_cls: DataDriver subclass
    :param env_varname: Name of enviromnent variable (or settings attribute) which holds connection string (e.g.: "mysql://user@pass@host/db")
    :type env_varname: str
    """

    _pool = {}

    @classmethod
    def select(cls, driver_cls, env_varname):
        """Return instance of driver.
        Selects instance from internal pool or creates new one.
        
        :param driver_cls: Driver class to instantiate it inside pool.
        :type driver_cls: DataDriver subclass
        :param env_varname: Name of enviromnent variable (or settings attribute) which holds connection string (e.g.: "mysql://user@pass@host/db")
        :type env_varname: str
        :raises ValueError: Pool for env_varname already exists
        :return: Instance of data driver
        :rtype: DataDriver
        """
        max_conn = getattr(driver_cls, "MAX_CONN", 3)
        pool_for_driver_cls = cls._pool.get(env_varname, None)

        if pool_for_driver_cls:
            if driver_cls != pool_for_driver_cls.driver_cls:
                raise ValueError(f"ConnectionPool: connection with name {env_varname} already registered for different class ({driver_cls} vs {pool_for_driver_cls.driver_cls})!")
        else:
            pool_for_driver_cls = ConnectionPool(driver_cls, env_varname)
            cls._pool[env_varname] = pool_for_driver_cls
        
        return next(pool_for_driver_cls)
    
    @classmethod
    def reset(cls):
        """Clean pool
        """
        import inspect
        import asyncio
        while cls._pool:
            name, conn = cls._pool.popitem()
            try:
                if inspect.isawaitable(conn.close):
                    loop = asyncio.get_event_loop()
                    future = asyncio.ensure_future(conn.close())
                    loop.run_until_complete(future)
                else:
                    conn.close()
            except Exception as e:
                log.error("Error on connection closing: %s", e)
            del conn
        log.info("Connection pool is clean now [Ok]")

    #: Alias for method    
    close = reset
    
    def __init__(self, driver_cls, env_varname):
        """Constructor method 
        """
        self.connections = []
        self.driver_cls = driver_cls
        self.env_varname = env_varname
        self.max_conn = getattr(driver_cls, "MAX_CONN", 3)
        self._nested_iter = None
    
    def __iter__(self):
        return self

    def __next__(self):
        "Round-Robin balancing"
        
        if len(self.connections) < self.max_conn:
            connection = self.driver_cls(self.env_varname)
            self.connections.append(connection)
            return connection

        if self._nested_iter is None:
            self._nested_iter = itertools.cycle(self.connections)

        return next(self._nested_iter)

@atexit.register
def close_all_connections():
    ConnectionPool.close()

class BaseQuery(object):
    """Base helper to define single operation with backend. 
    Implements "high-level" interface where connections are managed through connection pool.

    :param template: Template to build resource-specific query for operation. It can contain parameters.
    :type template: Any
    :param connection_alias: Connection name, which is related to connectin string in config.
    :type connection_alias: str
    :param driver: Driver class to instantiate it inside pool.
    :type driver: DataDriver subclass
    :param meta: Any user-defined data to store with this query, defaults to None
    :type meta: Mapping, optional
    """
    #: Default class for templates (e.g., it is str for SqlQuery)
    template_class = None

    def __init__(self, template, connection_alias, driver, meta=None):
        """Constructor method
        """
        # self.task_id = 'TASK_ID_DB_FETCH_' + self.name.upper()
        # print("QueriesSet - init instance", self)
        if self.template_class is None:
            raise TypeError("BaseQuery subclass should define its template_class member")
        if isinstance(template, self.template_class):
            self.template = template
            self.connection_alias = connection_alias
            self.driver = driver
            self.meta = meta
        else:
            raise TypeError(f"Invalid template class!")
    
    def _transform_params(self, params):
        "Encode params before passing them to request rendering"
        return params

    # def get_records(self, query_template, **params):
    #     """
    #     Return list of records
    #     """
    #     raise NotImplementedError()

    # def execute(self, query_template, **params):
    #     """
    #     Modify records in storage
    #     """
    #     raise NotImplementedError()


class ReaderMixin:
    """Request to read something.
    Applicable to BaseQuery descendants.
    Related to "read" operation.

    Note. It can change a state of the source implicitly in some cases (e.g., pop item from queue).
    """

    def get_records(self, **params): 
        """Fetch records from resource

        \**params: Parameters for request
        :return: List of records as a result of request/query
        :rtype: List[Dict[..]|NamedTuple]
        """
        params = self._transform_params(params)

        connection = ConnectionPool.select(self.driver, self.connection_alias)
        try:
            # log.debug(f"TRACE QUERY: {self.driver} | {self.connection_alias} | {self.template} ")
            return connection.get_records(self.template, **params)
        except Exception as e:
            log.error("Error with DB read: {!r}; SQL: {}".format(e, self.template))
            raise


class WriterMixin:
    """Explicit request to "change" (create, update, delete).
    Applicable to BaseQuery descendants.
    """

    def execute(self, **params) -> None:
        """Change data in resource.

        \**params: Parameters for request
        :return: Relay result of connection.execute for underlying driver (e.g. it can be number of records affected). This behaviour is driver-specific and can be changed in the future. It would be better to ignore this value.
        :rtype: Any
        """

        params = self._transform_params(params)

        connection = ConnectionPool.select(self.driver, self.connection_alias)
        try:
            # log.debug(f"TRACE QUERY: {self.driver} | {self.connection_alias} | {self.template} ")
            return connection.execute(self.template, **params)
        except Exception as e:
            log.error("Error with DB write: {!r}; SQL: {}".format(e, self.template))
            raise


class FixtureQuery(BaseQuery):
    """QA helper which returns fake response and logs requests.

    :param response_dict: Fake response
    :type response_dict: dict
    :param name: Name to trace requests in a log, defaults to None
    :type name: str, optional
    """
    def __init__(self, response_dict, name=None):
        """Constructor method
        """
        self.response_dict = response_dict
        self.name = name
    
    def get_records(self, **sql_params):
        """Return fake data to simulate DB response
        
        :return: Fake response
        :rtype: dict
        """
        return self.response_dict
    
    def execute(self, *args, **kwargs):
        """Dummy execute method.
        Writes request details to log.
        """
        log.info("Fake execute %s: %s %s", self.name, args, kwargs)


class debug(type):
    def __str__(self):
        return "{} {}".format(self.__name__, self.enum_queries())

class QueriesSet(metaclass=debug):
    """Template class to create sets of queries.
    Note that it descendants used directly as a class without instantiation.
    Queries should be defined as a class attributes.
    Subclasses of QueriesSet are "containers" to group queries together.
    Each application use single QueriesSet which contains different types of queries.
    Such approach allows to keep task function "clean" by means of "use" injector decorators and simplifies switching between fake (test) and production environment.

    Here is a quick example how we can organize our code:

    .. code-block:: python

        import os
        from fairways.io.generic import (QueriesSet,SqlQuery)
        from fairways.io.syn.sqlite import SqLite
        from fairways.decorators import (connection, entrypoint, use)
        from fairways.taskflow import Chain 

        # For illustration only:
        db_alias = 'db_sqlite_example'
        os.environ[db_alias] = ":memory:"

        @connection.define()
        class ExampleQueriesSet(QueriesSet):

            CREATE_TABLE = SqlQuery(
                \"""CREATE TABLE fairways (
                    id integer primary key,
                    name varchar
                );\""", 
                db_alias, 
                SqLite,
                ()
            )

            INSERT_DATA = SqlQuery(
                \"""INSERT INTO fairways (id, name) 
                    VALUES (1, "My Way");\""", 
                db_alias, 
                SqLite,
                ()
            )

            SELECT_DATA = SqlQuery(
                \"""SELECT name FROM fairways WHERE id=1;\""", 
                db_alias, 
                SqLite,
                ()
            )

            # You put here other types of queries here: 
            # HTTP, Redis, etc. ...

        @use.connection('dba')
        def create_table(ctx, dba=None):
            result = dba.CREATE_TABLE.execute()
            return ctx

        @use.connection('dba')
        def insert_data(ctx, dba=None):
            dba.INSERT_DATA.execute()
            return ctx

        @use.connection('dba')
        def select_data(ctx, dba=None):
            result = dba.SELECT_DATA.get_records()
            return {"result": result}

        def handle_error(err_info):
            log.error("ERROR: %r", err_info)

        def stop(ctx):
            log.info("Database operations done: %s", ctx)
            return {"result": "ok"}

        chain = Chain("DB example").then(
                create_table
            ).then(
                insert_data
            ).then(
                select_data
            ).then(
                stop
            ).catch(
                handle_error
            )

        @entrypoint.cmd(param='run')
        def run(ctx):
            result = chain({})
            log.info("Result: %s", result)

    """
    
    @classmethod
    def enum_queries(cls):
        """Enumerate queries.

        :return: Queries defined inside subclass
        :rtype: List[BaseQuery]
        """
        queries = []
        for attr_name, attr_value in cls.__dict__.items():
            if isinstance(attr_value, BaseQuery):
                queries.append(attr_name)
        return queries

    @classmethod
    def from_fixtures_dict(cls, name, item_factory=FixtureQuery, **items):
        attrs_dict = {}
        for attr_name, attr_value in items.items():
            attrs_dict.update({attr_name: item_factory(attr_value, attr_name)})
        parents = (cls, )
        return type(name, parents, attrs_dict)
    
    def __init__(self):
        raise TypeError("You do not need to instantiate QueriesSet and its subclasses!")

# class BaseQueryTemplate:

#     @abstractmethod
#     def render(self, *args, **kwargs):
#         pass

