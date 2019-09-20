# -*- coding: utf-8 -*-

import pymysql
import os
import re

from .dbi import DbDriver

import logging
log = logging.getLogger(__name__)

class MySql(DbDriver):

    @property
    def db_name(self):
        return self.conn_str.split("/")[-1]

    def _ensure_connection(self):
        if self.engine is None or not self.engine.open: 
            log.warning("Restoring DB connection: {}".format(self.db_name))
            self._connect()
    
    def _connect(self):
        user, password, host, port, database = re.match('mysql://(.*?):(.*?)@(.*?):(.*?)/(.*)', self.conn_str).groups()
        self.engine = pymysql.connect(
            host=host,
            user=user,
            password=password,                             
            db=database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True)


    def __init__(self, env_varname='DB_CONN', default='mysql://user:password@localhost:3306/nodb'):
        self.conn_str = os.getenv(env_varname, default)
        self.engine = None

        self._connect()
    
    def fetch(self,sql):
        try:
            self._ensure_connection()
            with self.engine.cursor() as cursor:
                cursor.execute(sql)
                res = cursor.fetchall()
            log.debug("SQL: %s",sql)
            return res
        except Exception as e:
            log.error("DB operation error: {} at {}".format(e, self.db_name))

    def change(self, sql):
        try:
            self._ensure_connection()
            with self.engine.cursor() as cursor:
                res = cursor.execute(sql)
            return res
        except Exception as e:
            log.error("DB operation error: {} at {}; \"{}\"".format(e, self.db_name, sql))

