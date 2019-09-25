# -*- coding: utf-8 -*-

import asyncio
import aiomysql
import os
import re

from .base import AsyncDbDriver

import logging
log = logging.getLogger(__name__)

class MySql(AsyncDbDriver):
    
    def is_connected(self):
        return self.engine and self.engine.open

    async def _connect(self):
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
        self.autoclose = True
