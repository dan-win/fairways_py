# -*- coding: utf-8 -*-
import os, sys

import logging
logging.basicConfig(
    # filename='example.log', 
    format='www_activity: %(asctime)s %(levelname)s:%(message)s', 
    level=logging.DEBUG)
log = logging.getLogger(__name__)

import re
import json
import itertools

import requests
import urllib

from hostapi.io import Heap, JsonStore, NullStore, Redis, Alchemy, MySql, ConnectionPool, json_stream

from hostapi.chains import Chain 

from hostapi.underscore import Underscore as _

SANDBOX_MODE = os.getenv('SANDBOX_MODE', False)

# engine = BinStore(buffer_path)
engine = NullStore()
heap = Heap(engine)
# jsonfile = JsonStore(buffer_path)

@heap.store
def fetch_trackers(ctx):
    """
    Extract data from remote buffer
    """

    redis_db =  ConnectionPool.select(Redis, "REDIS_ADDRESS") 

    trackers = []
    # Data exist in multiple chunks, so join them together by enumeration:
    while True:
        chunk = redis_db.engine.rpop("evt/enter")
        if chunk is None:
            break
        rec = chunk.decode()
        memdata = json.loads(rec)
        for event in memdata:
            trackers.append(event)

    return trackers

@heap.store
def handle_trackers(ctx):
    trackers = ctx
    if not ctx:
        return None
    for t in trackers:
        log.debug("-> {}".format(t))


def run(ctx):
    source = fetch_trackers
    dest = handle_trackers
    return run_with(source, dest)

# def test(ctx):
#     source = fake_trackers
#     dest = lambda ctx: ctx
#     return run_with(source, dest)

def run_with(source, dest):
    return Chain(
            source
        ).then(
        #     decode_trackers
        # ).then(
        #     fetch_db_transaction_operation
        # ).then(
        #     fetch_db_transaction
        # ).then(
        #     normalize_operations
        # ).then(
        #     explore_transactions
        # ).then(
        #     annotate_subject
        # ).then(
        #     encode_ga_ecomm_event
        # ).then(
            dest
        )
