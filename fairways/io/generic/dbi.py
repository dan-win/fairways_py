# -*- coding: utf-8 -*-

from .base import (BaseQuery, ReaderMixin, WriterMixin)
from fairways.funcflow import FuncFlow as ff

class SqlQuery(BaseQuery, ReaderMixin, WriterMixin):
    template_class = str
    
    def __init__(self, sql: str, connection_alias: str, driver, meta=None):
        """Creates new instance of DB task 
        
        Arguments:
            sql {str} -- Script to execute
            connection_alias {str} -- Name of environment variable wich holds config
            driver {DataDriver} -- DataDriver subclass
            meta {dict} -- Any data to store with the task instance
        """
        super().__init__(sql, connection_alias, driver, meta)

    def _transform_params(self, sql_params):
        def fmt_item(value, nested=True):
            if isinstance(value, (set, map, type({}.keys()))):
                value = list(value)
            if isinstance(value, (list, tuple)):
                s = ",".join(ff.map(value, fmt_item))
                if nested:
                    return "({})".format(s)
                return s

            # if isinstance(v, (set, map, list, tuple)):
            #     return self._transform_params(v)
            if isinstance(value, str):
                return "\"{}\"".format(value)
            if value is None:
                return "NULL"
            return str(value)
                
        # Convert lists to comma-delimited enumeration:
        for key, value in sql_params.items():
            sql_params[key] = fmt_item(value, nested=False)
        return sql_params



# __all__ = ["ConnectionPool", "DbTaskSetManager", "QueriesSet", "BaseQuery", "ReaderMixin", "WriterMixin", "FixtureQuery", "HttpQuery"]

# """High-level entities
# """

# import inspect
# import functools
# from contextlib import contextmanager
# from .types import (HttpQueryTemplate, HttpQueryParams)
# from typing import (List, Dict, NamedTuple)
# import logging
# log = logging.getLogger(__name__)

# class ConnectionPool:

#     _pool = {}

#     @classmethod
#     def select(cls, driver_cls, env_varname):
#         connection = cls._pool.get(env_varname)
#         if not connection:
#             connection = driver_cls(env_varname)
#             cls._pool[env_varname] = connection
#         # log.debug("Pool connections: {}".format(cls._pool))
#         return connection
    
# class BaseQuery(object):
#     template_class = None

#     def __init__(self, template, connection_alias, driver, meta=None):
#         """Creates new instance of Query 
        
#         Arguments:
#             template {any} -- Template (constant part) of query
#             connection_alias {str} -- Name of environment variable wich holds config
#             driver {DataDriver} -- DataDriver subclass
#             meta {dict} -- Any QA data to store with the task instance
#         """
#         # self.task_id = 'TASK_ID_DB_FETCH_' + self.name.upper()
#         # print("QueriesSet - init instance", self)
#         if self.template_class is None:
#             raise TypeError("BaseQuery subclass should define its template_class member")
#         if isinstance(template, self.template_class):
#             self.template = template
#             self.connection_alias = connection_alias
#             self.driver = driver
#             self.meta = meta
#         else:
#             raise TypeError(f"Invalid template class!")
    
#     def _transform_params(self, params):
#         "Encode params before passing them to request rendering"
#         return params

#     # def get_records(self, query_template, **params):
#     #     """
#     #     Return list of records
#     #     """
#     #     raise NotImplementedError()

#     # def execute(self, query_template, **params):
#     #     """
#     #     Modify records in storage
#     #     """
#     #     raise NotImplementedError()


# class ReaderMixin:
#     """Request to read something.
#     Applies to BaseQuery descendants.
#     Related to "read" operation.
#     Note. It can change a state of the source implicitly in some cases (e.g., pop item from queue).
#     """

#     def get_records(self, **params): # List[Dict[..]|NamedTuple], more: https://stackoverflow.com/a/50038614
#         """Fetch records from associated storage
        
#         Returns:
#             list -- List of records as a result of query
#         """

#         params = self._transform_params(params)

#         connection = ConnectionPool.select(self.driver, self.connection_alias)
#         try:
#             log.debug(f"TRACE QUERY: {self.driver} | {self.connection_alias} | {self.template} ")
#             return connection.get_records(self.template, **params)
#         except Exception as e:
#             log.error("Error with DB read: {!r}; SQL: {}".format(e, self.template))
#             raise



# class WriterMixin:
#     """Explicit request to "change" (create, update, delete).
#     Applies to BaseQuery descendants.
#     """

#     def execute(self, **params) -> None: # Throws errors if any
#         """Change data in associated storage
        
#         Returns:
#             int -- Number of records affected. 
#             This value can be ignored in future
#         """

#         params = self._transform_params(params)

#         connection = ConnectionPool.select(self.driver, self.connection_alias)
#         try:
#             log.debug(f"TRACE QUERY: {self.driver} | {self.connection_alias} | {self.template} ")
#             return connection.execute(self.template, **params)
#         except Exception as e:
#             log.error("Error with DB write: {!r}; SQL: {}".format(e, self.template))
#             raise




# class SqlQuery(BaseQuery, ReaderMixin, WriterMixin):
#     template_class = str
    
#     def __init__(self, sql: str, connection_alias: str, driver, meta=None):
#         """Creates new instance of DB task 
        
#         Arguments:
#             sql {str} -- Script to execute
#             connection_alias {str} -- Name of environment variable wich holds config
#             driver {DataDriver} -- DataDriver subclass
#             meta {dict} -- Any data to store with the task instance
#         """
#         super().__init__(sql, connection_alias, driver, meta)

#     def _transform_params(self, sql_params):
#         def fmt_item(value, nested=True):
#             if isinstance(value, (set, map, type({}.keys()))):
#                 value = list(value)
#             if isinstance(value, (list, tuple)):
#                 s = ",".join(ff.map(value, fmt_item))
#                 if nested:
#                     return "({})".format(s)
#                 return s

#             # if isinstance(v, (set, map, list, tuple)):
#             #     return self._transform_params(v)
#             if isinstance(value, str):
#                 return "\"{}\"".format(value)
#             if value is None:
#                 return "NULL"
#             return str(value)
                
#         # Convert lists to comma-delimited enumeration:
#         for key, value in sql_params.items():
#             sql_params[key] = fmt_item(value, nested=False)
#         return sql_params


# class FixtureQuery(BaseQuery):
#     def __init__(self, response_dict):
#         self.response_dict = response_dict
    
#     def get_records(self, **sql_params):
#         """ Return fixture data to simulate DB response"""
#         return self.response_dict
    
#     def execute(self, *args, **kwargs):
#         """ Dummy execute method"""
#         log.info("Fake execute: [%s] %s %s", self.name, args, kwargs)



# class HttpQuery(BaseQuery, ReaderMixin, WriterMixin):
#     template_class = HttpQueryTemplate
    
#     def _transform_params(self, params): # -> dict
#         path_args = params.get("path_args", {})
#         query_args = params.get("query_args", {})
#         data = params.get("data", None)
#         return self.template.render(data, *path_args, **query_args)


# class QueriesSetManager:
    
#     @property
#     def active(self):
#         return self.dba_reg[self.active_profile]

#     def __init__(self):
#         module = inspect.getmodule(inspect.stack()[1][0])
#         modname = module.__name__
#         self.modname = modname
#         self.dba_reg = {}
#         self.active_profile = None
    

#     # -> set_dba
#     def set_dba(self, dba_class):
#         if not issubclass(dba_class, QueriesSet):
#             raise TypeError("DBA class should be descendant of QueriesSet")
        
#         profile_name = dba_class.__name__
#         self._add_dba(profile_name, dba_class)
#         self.active_profile = profile_name

#     # -> create_dba_from_query_dict
#     def set_dba_from_query_dict(self, profile_name, **queries):
#         parents = (QueriesSet, )
#         for ff, query in queries.items():
#             if isinstance(query, BaseQuery):
#                 continue
#             raise TypeError("set_dba requires BaseQuery descendants in values of queries keyword arguments")
#         db_task_set = type(profile_name, parents, queries)
#         self._add_dba(profile_name, db_task_set)
#         self.active_profile = profile_name

#     def add_fixture(self, profile_name, **responses):
#         dba = self.from_dict(profile_name, item_factory=FixtureQuery, **responses)
#         self._add_dba(profile_name, dba)
    
#     def select_profile(self, profile_name):
#         """Select DBA profile to activate related DBA in manager instance
        
#         Arguments:
#             profile_name {[type]} -- [description]
        
#         Raises:
#             KeyError: [description]
        
#         Returns:
#             [type] -- [description]
#         """
#         found = self.dba_reg.get(profile_name)
#         if found:
#             saved = self.active_profile
#             self.active_profile = profile_name
#             return saved
#         raise KeyError("Cannot set profile {} because no such record in a registry".format(profile_name))
    
#     @contextmanager
#     def another_context(self, profile_name):
#         try:
#             initial_profile = self.select_profile(profile_name)
#             yield profile_name
#         finally:
#             # Code to release resource, e.g.:
#             self.select_profile(initial_profile)

#     def _add_dba(self, profile_name, dba):
#         def apply_names(dba):
#             for attr_name, attr_value in dba.__dict__.items():
#                 if isinstance(attr_value, BaseQuery):
#                     query_obj = attr_value
#                     setattr(query_obj, "name", attr_name)
            
#         if self.dba_reg.get(profile_name):
#             raise ValueError("DbTaskSetManager: QueriesSet with profile {} already defined for module {}".format(profile_name, self.modname))
#         apply_names(dba)
#         self.dba_reg[profile_name] = dba
    

#     # -> create_dba_from_attr_dict
#     @staticmethod
#     def from_dict(name, item_factory=lambda x:x, **items):
#         attrs_dict = {}
#         for attr_name, attr_value in items.items():
#             attrs_dict.update({attr_name: item_factory(attr_value)})
#         parents = (QueriesSet, )
#         return type(name, parents, attrs_dict)

#     @staticmethod
#     def inject_dba_decorator(manager, arg_name="dba"):
#         """Inject 'db' keyword argument into wrapped function.
#         Supports dynamic selection of the active QueriesSet immediately upon invocation of wrapped function.
#         Allows to use fixtures for tests
        
#         Arguments:
#             db {[type]} -- [description]
        
#         Returns:
#             callable -- Wrapped node
#         """
#         db = manager.active
#         # modname = modname.split('.')[-1]
#         # QueriesSet.set_module_db_taskset(db, modname)
#         def _decorator(func):
#             log.debug("@use_db: initial db set: %s", db.__name__)
#             @functools.wraps(func)
#             def wrapper(context, **kwargs):
#                 db = manager.active
#                 kwargs.update({'dba': db})
#                 log.debug("Switching DB: %s", db)
#                 return func(context, **kwargs)
#             return wrapper
#         return _decorator


# class debug(type):
#     def __str__(self):
#         return "{} {}".format(self.__name__, self.enum_queries())

# class QueriesSet(metaclass=debug):
#     """Template class to create sets of DB tasks
    
#     Arguments:
#         object {[type]} -- [description]
    
#     Returns:
#         [type] -- [description]
#     """
#     @classmethod
#     def enum_queries(cls):
#         queries = []
#         for attr_name, attr_value in cls.__dict__.items():
#             if isinstance(attr_value, BaseQuery):
#                 queries.append(attr_name)
#         return queries


