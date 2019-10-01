# -*- coding: utf-8 -*-

import pymysql
import re

from .base import (SynDataDriver, UriConnMixin)

import logging
log = logging.getLogger(__name__)

class MySql(SynDataDriver, UriConnMixin):

    autoclose = False

    def is_connected(self):
        return self.engine and self.engine.open
    
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
    


