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

from .base import (SynDataDriver, UriConnMixin)

import logging
log = logging.getLogger(__name__)

class PostgreSql(SynDataDriver, UriConnMixin):

    autoclose = False

    def is_connected(self):
        return self.engine and not self.engine.closed
    
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
            raise

    def change(self, sql):
        try:
            self._ensure_connection()
            with self.engine.cursor(cursor_factory=_DictCursor) as cursor:
                res = cursor.execute(sql)
            return res
        except Exception as e:
            log.error("DB operation error: {} at {}; \"{}\"".format(e, self.db_name, sql))
            raise

