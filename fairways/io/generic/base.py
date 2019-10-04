# -*- coding: utf-8 -*-

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
]

"""High-level entities
"""

import inspect
import functools
from contextlib import contextmanager
from typing import (List, Dict)
from collections import namedtuple

from fairways.decorators import use

import logging
log = logging.getLogger(__name__)

import os
import sys
import re

CONF_KEY = "CONNECTIONS"

RE_ENV_EXPRESSION = re.compile(r"\{\$(.*?)\}")
# RE_URI_TEMPLATE = re.compile(r"(.*?)://(.*?):(.*?)@(.*?):(.*?)/(.*)")
# RE_URI_TEMPLATE = re.compile(r"(.*?)://(.*?):(.*?)@(.*?):(.*?)/(.*)")
RE_URI_TEMPLATE = re.compile(r"(?P<scheme>.*?)://(?:(?P<user>[^:]*):(?P<password>[^@]*)@)?(?P<host>[^:^/]*)(?::(?P<port>[^/|^?]*))?(?:/(?P<path>.*))?")

UriParts = namedtuple('UriParts', 'scheme,user,password,host,port,path'.split(','))

# this is a pointer to the module object instance itself.
this = sys.modules[__name__]
this._config_provider = os.environ

@use.config(CONF_KEY)
def set_config_provider(config_dict):
    prev_value = this._config_provider
    if config_dict:
        this._config_provider = config_dict
    return prev_value

def replace_env_vars(s):
    """Replace all occurences of {$name} in string with values from os.environ
    
    Arguments:
        s {[str]} -- [description]
    
    Returns:
        [str] -- [String with replaced values]
    """
    def envrepl(match):
        (env_var,) = match.groups(1)
        return os.environ[env_var]

    return RE_ENV_EXPRESSION.sub(envrepl, s)

def parse_conn_uri(s):
    """Split uri to parts:
    sheme, use, password, host, port, path.
    Absent parts replaced with None
    
    Arguments:
        s {[str]} -- [uri]
    
    Returns:
        [UriParts] -- [Parsed uri]
    """
    match = RE_URI_TEMPLATE.match(s)
    m = match.group
    return UriParts(m('scheme'), m('user'), m('password'), m('host'), m('port'), m('path'))


class UriConnMixin:
    def _parse_uri(self, conn_uri):
        """Returns UriParts tuple
        
        Arguments:
            conn_uri {str} -- [description]
        
        Returns:
            [UriParts] -- Parts of uri
        """
        return parse_conn_uri(conn_uri)

class FileConnMixin:
    def _parse_uri(self, conn_uri):
        """Returns UriParts tuple
        
        Arguments:
            conn_uri {str} -- [description]
        
        Returns:
            [UriParts] -- Parts of uri
        """
        return UriParts(None, None, None, None, None, conn_uri)


class DataDriver:
    """Base class for database driver
    
    Raises:
        NotImplementedError: [description]
        NotImplementedError: [description]
        NotImplementedError: [description]
    
    Returns:
        [type] -- [description]
    """
    default_conn_str = ""
    autoclose = False

    _config_provider = os.environ

    @classmethod
    def set_config_provider(cls, config_dict):
        prev_value = cls._config_provider
        cls._config_provider = config_dict
        return prev_value

    @property
    def db_name(self):
        return self.conn_str.split("/")[-1]
    
    def is_connected(self):
        raise NotImplementedError(f"Override is_connected for {self.__class__.__name__}")
    
    def __init__(self, env_varname):
        """Constructor
        
        Arguments:
            env_varname {str} -- Name of enviromnent variable which holds connection string (e.g.: "mysql://user@pass@host/db")
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

    # def fetch(self, sql):
    #     raise NotImplementedError()

    # def change(self, sql):
    #     raise NotImplementedError()

    def get_records(self, query_template, **params):
        """
        Return list of records. 
        This method is common for sync and async implementations (in latter case it acts as a proxy for awaitable)
        """
        # Convert all iterables to lists to 
        query = query_template.format(**params).replace('\n', " ").replace("\"", "\'")
        # log.debug("SQL: {}".format(query))
        return self.fetch(query)

    def execute(self, query_template, **params):
        """
        Modify records in storage
        This method is common for sync and async implementations (in latter case it acts as a proxy for awaitable)
        """
        query = query_template.format(**params)
        # log.debug("SQL: {}".format(query))
        return self.change(query)



class ConnectionPool:

    _pool = {}

    @classmethod
    def select(cls, driver_cls, env_varname):
        connection = cls._pool.get(env_varname)
        if connection:
            if driver_cls != connection.__class__:
                raise ValueError(f"ConnectionPool: connection with name {env_varname} already registered for different class ({driver_cls} vs {connection.__class__})!")
        else:
            connection = driver_cls(env_varname)
            cls._pool[env_varname] = connection

        # log.debug("Pool connections: {}".format(cls._pool))
        return connection
    
    @classmethod
    def reset(cls):
        while self._pool:
            name, conn = self._pool.popitem()
            del conn


class BaseQuery(object):
    template_class = None

    def __init__(self, template, connection_alias, driver, meta=None):
        """Creates new instance of Query 
        
        Arguments:
            template {any} -- Template (constant part) of query
            connection_alias {str} -- Name of environment variable wich holds config
            driver {DataDriver} -- DataDriver subclass
            meta {dict} -- Any QA data to store with the task instance
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
    Applies to BaseQuery descendants.
    Related to "read" operation.
    Note. It can change a state of the source implicitly in some cases (e.g., pop item from queue).
    """

    def get_records(self, **params): # List[Dict[..]|NamedTuple], more: https://stackoverflow.com/a/50038614
        """Fetch records from associated storage
        
        Returns:
            list -- List of records as a result of query
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
    Applies to BaseQuery descendants.
    """

    def execute(self, **params) -> None: # Throws errors if any
        """Change data in associated storage
        
        Returns:
            int -- Number of records affected. 
            This value can be ignored in future
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
    def __init__(self, response_dict, name=None):
        self.response_dict = response_dict
        self.name = name
    
    def get_records(self, **sql_params):
        """ Return fixture data to simulate DB response"""
        return self.response_dict
    
    def execute(self, *args, **kwargs):
        """ Dummy execute method"""
        log.info("Fake execute %s: %s %s", self.name, args, kwargs)


class debug(type):
    def __str__(self):
        return "{} {}".format(self.__name__, self.enum_queries())

class QueriesSet(metaclass=debug):
    """Template class to create sets of DB tasks
    
    Arguments:
        object {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    @classmethod
    def enum_queries(cls):
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