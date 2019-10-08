# -*- coding: utf-8 -*-

import redis
import os
import re
import json 
from .base import (SynDataDriver, UriConnMixin)

import logging
log = logging.getLogger(__name__)


class Redis(SynDataDriver, UriConnMixin):
    autoclose = False
    default_conn_str = 'localhost:6379'

    def is_connected(self):
        return self.engine
    
    def _connect(self):
        redis_host, redis_port = self.uri_parts.host, self.uri_parts.port
        # uri parts
        self.engine = redis.StrictRedis(host=redis_host, port=int(redis_port), db=0)

    def get_records(self, data_key, **params):
        self._ensure_connection()
        records = []
        # Data exist in multiple chunks, so join them together by enumeration:
        chunk = self.engine.rpop(data_key)
        if chunk:
            rec = chunk.decode()
            memdata = json.loads(rec)
            for event in memdata:
                records.append(event)

        return records


class RedisStack(Redis):
    """
    Simple read-only facility which uses RPOP command.
    Data stored in arrays which are values of hash tree.
    """

    def get_records(self, data_key, **params):
        self._ensure_connection()
        records = []
        # Data exist in multiple chunks, so join them together by enumeration:
        while True:
            chunk = self.engine.rpop(data_key)
            if chunk is None:
                break
            rec = chunk.decode()

            memdata = json.loads(rec)
            for event in memdata:
                records.append(event)
                # Entract IDs here, signle dict with "type" keys

        return records

