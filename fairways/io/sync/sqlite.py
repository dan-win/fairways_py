# -*- coding: utf-8 -*-

import sqlite3
import os
import re

from .base import SynDataDriver

import logging
log = logging.getLogger(__name__)

class SqLite(SynDataDriver):

    default_conn_str = ":memory:"
    autoclose = True

    def is_connected(self):
        return self.engine is not None

    def _connect(self):
        db_filename = self.conn_str
        engine = sqlite3.connect(db_filename)
        engine.row_factory = dict_factory
        engine.isolation_level = "IMMEDIATE"
        self.engine = engine

    def fetch(self,sql):
        cursor = None
        try:
            self._ensure_connection()
            cursor = self.engine.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            log.error("DB operation error: {} at {}".format(e, self.db_name))
            raise
        finally:
            if cursor:
                cursor.close()
            if self.autoclose:
                self.close()

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
