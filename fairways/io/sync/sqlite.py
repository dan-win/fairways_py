# -*- coding: utf-8 -*-

import sqlite3
import os
import re

from .dbi import DbDriver

import logging
log = logging.getLogger(__name__)

class SqLite(DbDriver):
    @property
    def db_name(self):
        return self.conn_str.split("/")[-1]

    def _ensure_connection(self):
        if not self.engine: 
            log.warning("Restoring DB connection: {}".format(self.db_name))
            self._connect()
    
    def _connect(self):
        db_filename = self.conn_str
        self.engine = sqlite3.connect(db_filename)
        self.engine.islolation_level = "IMMEDIATE"


    def __init__(self, env_varname='DB_CONN', default=":memory:"):
        self.conn_str = os.getenv(env_varname, default)
        assert self.conn_str, "SqLite error: you should specify either environment variable or default value for database file name"
        self.engine = None
            
    def fetch(self,sql):
        try:
            self._ensure_connection()
            with self.engine.cursor() as cursor:
                cursor.execute(sql)
                res = cursor.fetchall()
            return res
        except Exception as e:
            log.error("DB operation error: {} at {}".format(e, self.db_name))
        finally:
            self.engine.close()
            self.engine = None

    def change(self, sql):
        try:
            self._ensure_connection()
            with self.engine.cursor() as cursor:
                res = cursor.execute(sql)
            return res
        except Exception as e:
            log.error("DB operation error: {} at {}; {}".format(e, self.db_name, sql))
        finally:
            self.engine.commit()
            self.engine.close()
            self.engine = None


