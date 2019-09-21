# -*- coding: utf-8 -*-

import redis
import os
import re

from .dbi import DbDriver

import logging
log = logging.getLogger(__name__)


class Redis(DbDriver):
    def __init__(self, env_varname='REDIS_ADDRESS', default='localhost:6379'):
        redis_host, redis_port = os.getenv(env_varname, default).split(":")
        self.engine = redis.StrictRedis(host=redis_host, port=int(redis_port), db=0)


class RedisStack(Redis):
    """
    Simple read-only facility which uses RPOP command.
    Data stored in arrays which are values of hash tree.
    """

    def get_records(self, data_key, **params):

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

