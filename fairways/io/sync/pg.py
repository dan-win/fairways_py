# -*- coding: utf-8 -*-

try:
    # Used for compatibility with PyPy. 
    from psycopg2cffi import compat
    compat.register()
    from psycopg2.extras import DictCursor as _DictCursor
    POSTGRES_AVAILABLE =True
except:
    POSTGRES_AVAILABLE =False

import os
import re

from .dbi import DbDriver

import logging
log = logging.getLogger(__name__)

class PostgreSql(DbDriver):

    @property
    def db_name(self):
        return self.conn_str.split("/")[-1]

    def _ensure_connection(self):
        if self.engine is None or self.engine.closed: 
            log.warning("Restoring DB connection: {}".format(self.db_name))
            self._connect()
    
    def _connect(self):
        user, password, host, port, database = re.match('postgres[^:]*://(.*?):(.*?)@(.*?):(.*?)/(.*)', self.conn_str).groups()
        self.engine = psycopg2.connect(
            host=host,
            user=user,
            password=password,                             
            db=database,
            charset='utf8mb4',
            # cursorclass=_DictCursor,
            autocommit=True)

    def __init__(self, env_varname='DATABASE_URL', default='localhost:5432'):
        self.conn_str = os.getenv(env_varname, default)
        self.engine = None
        self._connect()
    
    def __del__(self):
        if self:
            self.close()
    
    def close(self):
        if self.engine and not self.engine.closed:
            self.engine.close()
            self.engine = None
    
    def fetch(self,sql):
        try:
            self._ensure_connection()
            with self.engine.cursor(cursor_factory=_DictCursor) as cursor:
                cursor.execute(sql)
                res = cursor.fetchall()
            log.debug("SQL: %s",sql)
            return res
        except Exception as e:
            log.error("DB operation error: {} at {}".format(e, self.db_name))

    def change(self, sql):
        try:
            self._ensure_connection()
            with self.engine.cursor(cursor_factory=_DictCursor) as cursor:
                res = cursor.execute(sql)
            return res
        except Exception as e:
            log.error("DB operation error: {} at {}; \"{}\"".format(e, self.db_name, sql))

