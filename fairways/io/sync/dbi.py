# -*- coding: utf-8 -*-

__all__ = ["ConnectionPool", "DbTaskSetManager", "DbTaskSet", "DbDriver", "Query", "FixtureQuery"]

import inspect
import functools
from contextlib import contextmanager
from enum import Enum
import logging
log = logging.getLogger(__name__)

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
    
class BaseQuery(object):
    def get_records(self, query_template, **params):
        """
        Return list of records
        """
        raise NotImplementedError()

    def execute(self, query_template, **params):
        """
        Modify records in storage
        """
        raise NotImplementedError()


class Query(BaseQuery):
    def __init__(self, sql, db_env_conf, driver, meta=None):
        """Creates new instance of DB task 
        
        Arguments:
            sql {str} -- Script to execute
            db_env_conf {str} -- Name of environment variable wich holds config
            driver {DbDriver} -- DbDriver subclass
            meta {dict} -- Any data to store with the task instance
        """
        # self.task_id = 'TASK_ID_DB_FETCH_' + self.name.upper()
        # print("DbTaskSet - init instance", self)
        self.sql = sql
        self.db_env_conf = db_env_conf
        self.driver = driver
        self.meta = meta
    
    def _transform_params(self, sql_params):
        def fmt_item(value, nested=True):
            if isinstance(value, (set, map, type({}.keys()))):
                value = list(value)
            if isinstance(value, (list, tuple)):
                s = ",".join(_.map(value, fmt_item))
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
                
    def get_records(self, **sql_params):
        """Fetch records from associated storage
        
        Returns:
            list -- List of records as a result of query
        """

        sql_params = self._transform_params(sql_params)

        db = ConnectionPool.select(self.driver, self.db_env_conf)
        try:
            return db.get_records(self.sql, **sql_params)
        except Exception as e:
            log.error("Error with DB read: {!r}; SQL: {}".format(e, self.sql))
            raise


    def execute(self, **sql_params):
        """Change data in associated storage
        
        Returns:
            int -- Number of records affected. 
            This value can be ignored in future
        """

        sql_params = self._transform_params(sql_params)

        db = ConnectionPool.select(self.driver, self.db_env_conf)
        try:
            return db.execute(self.sql, **sql_params)
        except Exception as e:
            log.error("Error with DB write: {!r}; SQL: {}".format(e, self.sql))
            raise


class FixtureQuery(BaseQuery):
    def __init__(self, response_dict):
        self.response_dict = response_dict
    
    def get_records(self, **sql_params):
        """ Return fixture data to simulate DB response"""
        return self.response_dict
    
    def execute(self, *args, **kwargs):
        """ Dummy execute method"""
        log.info("Fake execute: [%s] %s %s", self.name, args, kwargs)


# class DbType(type):
#     def __getattr__(cls, key):
#         if key != "__queries":
#             value = getattr(cls, "__queries").get(key)
#             if value:
#                 return value


class DbTaskSetManager:
    
    @property
    def active(self):
        return self.dba_reg[self.active_profile]

    def __init__(self):
        module = inspect.getmodule(inspect.stack()[1][0])
        modname = module.__name__
        self.modname = modname
        self.dba_reg = {}
        self.active_profile = None
    

    # -> set_dba
    def set_dba(self, dba_class):
        if not issubclass(dba_class, DbTaskSet):
            raise TypeError("DBA class should be descendant of DbTaskSet")
        
        profile_name = dba_class.__name__
        self._add_dba(profile_name, dba_class)
        self.active_profile = profile_name

    # -> create_dba_from_query_dict
    def set_dba_from_query_dict(self, profile_name, **queries):
        parents = (DbTaskSet, )
        for _, query in queries.items():
            if isinstance(query, BaseQuery):
                continue
            raise TypeError("set_dba requires BaseQuery descendants in values of queries keyword arguments")
        db_task_set = type(profile_name, parents, queries)
        self._add_dba(profile_name, db_task_set)
        self.active_profile = profile_name

    def add_fixture(self, profile_name, **responses):
        dba = self.from_dict(profile_name, item_factory=FixtureQuery, **responses)
        self._add_dba(profile_name, dba)
    
    def select_profile(self, profile_name):
        """Select DBA profile to activate related DBA in manager instance
        
        Arguments:
            profile_name {[type]} -- [description]
        
        Raises:
            KeyError: [description]
        
        Returns:
            [type] -- [description]
        """
        found = self.dba_reg.get(profile_name)
        if found:
            saved = self.active_profile
            self.active_profile = profile_name
            return saved
        raise KeyError("Cannot set profile {} because no such record in a registry".format(profile_name))
    
    @contextmanager
    def another_context(self, profile_name):
        try:
            initial_profile = self.select_profile(profile_name)
            yield profile_name
        finally:
            # Code to release resource, e.g.:
            self.select_profile(initial_profile)

    def _add_dba(self, profile_name, dba):
        def apply_names(dba):
            for attr_name, attr_value in dba.__dict__.items():
                if isinstance(attr_value, BaseQuery):
                    query_obj = attr_value
                    setattr(query_obj, "name", attr_name)
            
        if self.dba_reg.get(profile_name):
            raise ValueError("DbTaskSetManager: DbTaskSet with profile {} already defined for module {}".format(profile_name, self.modname))
        apply_names(dba)
        self.dba_reg[profile_name] = dba
    

    # -> create_dba_from_attr_dict
    @staticmethod
    def from_dict(name, item_factory=lambda x:x, **items):
        attrs_dict = {}
        for attr_name, attr_value in items.items():
            attrs_dict.update({attr_name: item_factory(attr_value)})
        parents = (DbTaskSet, )
        return type(name, parents, attrs_dict)

    @staticmethod
    def inject_dba_decorator(manager, arg_name="dba"):
        """Inject 'db' keyword argument into wrapped function.
        Supports dynamic selection of the active DbTaskSet immediately upon invocation of wrapped function.
        Allows to use fixtures for tests
        
        Arguments:
            db {[type]} -- [description]
        
        Returns:
            callable -- Wrapped node
        """
        db = manager.active
        # modname = modname.split('.')[-1]
        # DbTaskSet.set_module_db_taskset(db, modname)
        def _decorator(func):
            log.debug("@use_db: initial db set: %s", db.__name__)
            @functools.wraps(func)
            def wrapper(context, **kwargs):
                db = manager.active
                kwargs.update({'dba': db})
                log.debug("Switching DB: %s", db)
                return func(context, **kwargs)
            return wrapper
        return _decorator


class debug(type):
    def __str__(self):
        return "{} {}".format(self.__name__, self.enum_queries())

class DbTaskSet(metaclass=debug):
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

    # def __new__(cls):
    #     log.debug("Instantiation: __new__ called for: %s", cls.__name__)
    #     for attr_name, attr_value in cls.__dict__.items():
    #         if isinstance(attr_value, BaseQuery):
    #             setattr(query, "name", attr_name)

    #     return object.__new__(cls)

    # _db_task_set_registry = {}

    # @staticmethod
    # def create_dba(profile_name, **queries):
    #     module = inspect.getmodule(inspect.stack()[1][0])
    #     modname = module.__name__
    #     if hasattr(module, "__dba__"):
    #         raise TypeError("Module {} already has __dba__ member!")
    #     parents = (DbTaskSet, )
    #     db_task_set = type(profile_name, parents, queries)

    #     __dba__ = DbTaskSetManager(db_task_set, profile_name, modname)
    #     log.debug("creating DbTaskSetManager for module %s", modname)
    #     setattr(module, "__dba__", __dba__)

    #     # definer_modname = modname.split('.')[-1]
    #     # if DbTaskSet._db_task_set_registry.get(definer_modname):
    #     #     log.warning("DbTaskSet for module '%s' already defined: '%s'", definer_modname, cls.enum_queries())
    #     # DbTaskSet._db_task_set_registry[definer_modname] = cls
    #     # return db_task_set


    # @classmethod
    # def from_dict(cls, name, item_factory=lambda x:x, **items):
    #     attrs_dict = {}
    #     for attr_name, attr_value in items.items():
    #         attrs_dict.update({attr_name: item_factory(attr_value)})
    #     parents = (DbTaskSet, )
    #     return type(name, parents, attrs_dict)

    # def __new__(cls):
    #     modname = cls.__module__
    #     definer_modname = modname.split('.')[-1]
    #     print("DEFINER MODULE", definer_modname)
    #     if DbTaskSet._db_task_set_registry.get(definer_modname):
    #         log.warning("DbTaskSet for module '%s' already defined: '%s'", definer_modname, cls.enum_queries())
    #     DbTaskSet._db_task_set_registry[definer_modname] = cls

    #     return object.__new__(cls)

    # @staticmethod
    # def get_module_db_taskset(modname=None):
    #     if modname is None:
    #         modname = inspect.getmodule(inspect.stack()[1][0]).__name__
    #     modname = modname.split('.')[-1]
    #     try:
    #         prev = DbTaskSet._db_task_set_registry[modname]
    #     except KeyError:
    #         log.error("No DbTaskSet subclass defined in module '%s'", modname)
    #         raise
    #     return prev

    # @staticmethod
    # def set_module_db_taskset(new_cls, modname=None):
    #     if modname is None:
    #         modname = inspect.getmodule(inspect.stack()[1][0]).__name__
    #     modname = modname.split('.')[-1]
    #     prev = DbTaskSet._db_task_set_registry.get(modname)
    #     DbTaskSet._db_task_set_registry.update({modname: new_cls})
    #     log.warning("Overriding DbTaskSet subclass '%s' with '%s' for module '%s'", prev and prev.__name__ or None, new_cls.__name__, modname)
    #     return prev

    # @staticmethod
    # def new_fixture(name, **fixture):
    #     modname = inspect.getmodule(inspect.stack()[1][0]).__name__
    #     modname = modname.split('.')[-1]
    #     attrs_dict = {}
    #     for attr_name, response in fixture.items():
    #         attrs_dict[attr_name] = FixtureQuery(response)
    #     parents = (DbTaskSet, )
    #     return type(name, parents, attrs_dict)
    
    # @staticmethod
    # def weld_db(db):
    #     """Inject 'db' keyword argument into wrapped function statically.
        
    #     Arguments:
    #         db {[type]} -- [description]
        
    #     Returns:
    #         callable -- Wrapped node
    #     """
    #     def decorator(func):
    #         @functools.wraps(func)
    #         def wrapper(context, **kwargs):
    #             print("Signature: ", signature(func), "| env: ", env_vector)
    #             kwargs.update({"db": db})
    #             return func(context, **kwargs)
    #         return wrapper
    #     return decorator


    # @staticmethod
    # def use_db(dba_name, varname='db', module=None):
    #     """Inject 'db' keyword argument into wrapped function.
    #     Supports dynamic selection of the active DbTaskSet immediately upon invocation of wrapped function.
    #     Allows to use fixtures for tests
        
    #     Arguments:
    #         db {[type]} -- [description]
        
    #     Returns:
    #         callable -- Wrapped node
    #     """
    #     calling_module = inspect.getmodule(inspect.stack()[1][0])
    #     if module is None:
    #         module = calling_module
    #     local_dba = module.__dba__
    #     db = local_dba.active
    #     # modname = modname.split('.')[-1]
    #     # DbTaskSet.set_module_db_taskset(db, modname)
    #     def decorator(func):
    #         log.debug("@use_db: initial db set: %s", db.__name__)
    #         @functools.wraps(func)
    #         def wrapper(context, **kwargs):
    #             db = local_dba.active
    #             kwargs.update({varname: db})
    #             log.debug("Switching DB: %s", db)
    #             return func(context, **kwargs)
    #         return wrapper
    #     return decorator


    # # @staticmethod
    # # def use_db(db, varname='db'):
    # #     """Inject 'db' keyword argument into wrapped function.
    # #     Supports dynamic selection of the active DbTaskSet immediately upon invocation of wrapped function.
    # #     Allows to use fixtures for tests
        
    # #     Arguments:
    # #         db {[type]} -- [description]
        
    # #     Returns:
    # #         callable -- Wrapped node
    # #     """
    # #     modname = inspect.getmodule(inspect.stack()[1][0]).__name__
    # #     modname = modname.split('.')[-1]
    # #     DbTaskSet.set_module_db_taskset(db, modname)
    # #     def decorator(func):
    # #         log.debug("@use_db: initial db set: %s", db.__name__)
    # #         @functools.wraps(func)
    # #         def wrapper(context, **kwargs):
    # #             db = DbTaskSet.get_module_db_taskset(modname)
    # #             kwargs.update({varname: db})
    # #             log.debug("Switching DB: %s", db)
    # #             return func(context, **kwargs)
    # #         return wrapper
    # #     return decorator


# class DbTaskSet(Enum):

#     def __init__(self, sql, db_env_conf, driver, meta):
#         """Creates new instance of DB task 
#         Note: class is based on Python Enum so
#         __init__ blesses a single member of enumeration
#         (See more about Python Enum class)
        
#         Arguments:
#             sql {str} -- Script to execute
#             db_env_conf {str} -- Name of environment variable wich holds config
#             driver {DbDriver} -- DbDriver subclass
#             meta {dict} -- Any data to store with the task instance
#         """
#         # self.task_id = 'TASK_ID_DB_FETCH_' + self.name.upper()
#         # print("DbTaskSet - init instance", self)
#         self.sql = sql
#         self.db_env_conf=db_env_conf
#         self.driver = driver
#         self.meta = meta
    
#     def _transform_params(self, sql_params):
#         def fmt_item(value, nested=True):
#             if isinstance(value, (set, map, type({}.keys()))):
#                 value = list(value)
#             if isinstance(value, (list, tuple)):
#                 s = ",".join(_.map(value, fmt_item))
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
                
#     def get_records(self, **sql_params):
#         """Fetch records from associated storage
        
#         Returns:
#             list -- List of records as a result of query
#         """

#         sql_params = self._transform_params(sql_params)

#         db = ConnectionPool.select(self.driver, self.db_env_conf)
#         try:
#             return db.get_records(self.sql, **sql_params)
#         except Exception as e:
#             log.error("Error with DB read: {!r}; SQL: {}".format(e, self.sql))
#             raise


#     def execute(self, **sql_params):
#         """Change data in associated storage
        
#         Returns:
#             int -- Number of records affected. 
#             This value can be ignored in future
#         """

#         sql_params = self._transform_params(sql_params)

#         db = ConnectionPool.select(self.driver, self.db_env_conf)
#         try:
#             return db.execute(self.sql, **sql_params)
#         except Exception as e:
#             log.error("Error with DB write: {!r}; SQL: {}".format(e, self.sql))
#             raise


class DbDriver:
    def fetch(self, sql):
        raise NotImplementedError()

    def change(self, sql):
        raise NotImplementedError()

    def get_records(self, query_template, **params):
        """
        Return list of records
        """
        # Convert all iterables to lists to 
        query = query_template.format(**params).replace('\n', " ").replace("\"", "\'")
        # log.debug("SQL: {}".format(query))
        return self.fetch(query)

    def execute(self, query_template, **params):
        """
        Modify records in storage
        """
        query = query_template.format(**params)
        # log.debug("SQL: {}".format(query))
        return self.change(query)
