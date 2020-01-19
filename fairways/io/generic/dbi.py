# -*- coding: utf-8 -*-
""" Query to database """
from .base import (BaseQuery, ReaderMixin, WriterMixin)
from fairways.funcflow import FuncFlow as ff

class SqlQuery(BaseQuery, ReaderMixin, WriterMixin):
    """SQL query to database.

    :param sql: SQL script with parameters in "{name}" format
    :type sql: str
    :param connection_alias: Connection name, which is related to connectin string in config.
    :type connection_alias: str
    :param driver: Driver class to instantiate it inside pool.
    :type driver: DataDriver subclass
    :param meta: Any user-defined data to store with this query, defaults to None
    :type meta: Mapiing, optional
    """
    
    #: Template type for SQL is a string
    template_class = str
    
    def __init__(self, sql: str, connection_alias: str, driver, meta=None):
        """Constructor method
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





