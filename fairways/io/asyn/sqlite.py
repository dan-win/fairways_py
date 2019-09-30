# -*- coding: utf-8 -*-

import asyncio
import aiosqlite
import os
import re

from .base import AsyncDataDriver
# Should provice async methods .fetch, .execute

import logging
log = logging.getLogger(__name__)

class SqLite(AsyncDataDriver):
    default_conn_str = ":memory:"
    autoclose = True

    def is_connected(self):
        return self.engine is not None

    async def _connect(self):
        db_filename = self.conn_str
        engine = await aiosqlite.connect(db_filename)
        engine.row_factory = dict_factory
        engine.isolation_level = "IMMEDIATE"
        self.engine = engine


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
