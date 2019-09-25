# -*- coding: utf-8 -*-

import asyncio
import aiosqlite
import os
import re

from .base import AsyncDbDriver
# Should provice async methods .fetch, .execute

import logging
log = logging.getLogger(__name__)

class SqLite(AsyncDbDriver):

    def is_connected(self):
        return self.engine is not None

    async def _connect(self):
        db_filename = self.conn_str
        engine = await aiosqlite.connect(db_filename)
        engine.row_factory = dict_factory
        engine.isolation_level = "IMMEDIATE"
        self.engine = engine
    
    async def close(self):
        if self.engine is not None:
            await self.engine.close()
            self.engine = None

    def __init__(self, env_varname='DB_CONN', default=":memory:"):
        self.conn_str = os.getenv(env_varname, default)
        self.engine = None
        assert self.conn_str, "SqLite error: you should specify either environment variable or default value for database file name"
        self.autoclose = True


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
