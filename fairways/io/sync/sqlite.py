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
    
    def _connect(self):
        db_filename = self.conn_str
        engine = sqlite3.connect(db_filename)
        engine.row_factory = dict_factory
        engine.isolation_level = "IMMEDIATE"
        return engine

    def __init__(self, env_varname='DB_CONN', default=":memory:"):
        self.conn_str = os.getenv(env_varname, default)
        self.lock_count = 0
            
    def fetch(self,sql):
        db = None
        try:
            db = self._connect()
            with db.execute(sql) as cursor:
                return cursor.fetchall()
        except Exception as e:
            log.error("DB operation error: {} at {}".format(e, self.db_name))
            raise
        finally:
            if db:
                db.close()

    def change(self, sql):
        db = None
        try:
            db = self._connect()
            db.execute(sql)
            db.commit()
            return None
        except Exception as e:
            log.error("DB operation error: {} at {}; {}".format(e, self.db_name, sql))
            raise
        finally:
            if db:
                db.close()


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
