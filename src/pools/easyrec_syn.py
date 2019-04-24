# -*- coding: utf-8 -*-
"""
Updates catalog in easyrec
"""
import os, sys

import logging
logging.basicConfig(
    # filename='example.log', 
    format='easyrec_syn: %(asctime)s %(levelname)s:%(message)s', 
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

buffer_path = os.getenv('EVENTMACHINE_BUFFER', './../buffer')
# engine = BinStore(buffer_path)
engine = NullStore()
heap = Heap(engine)
jsonfile = JsonStore(buffer_path)


@heap.store
def check_er_catalog_state(ctx):
    pass

def check_tvz_catalog_state(ctx):
    pass

