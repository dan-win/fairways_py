# -*- coding: utf-8 -*-
"""
Updates catalog in easyrec
"""
import os, sys

import logging

log = logging.getLogger(__name__)

import re
import json
import csv
import itertools

import requests
import urllib

from enum import Enum, IntEnum

import fairways

from fairways.io.sync import JsonStore, NullStore, Redis, MySql, ConnectionPool, DbTaskSetManager, DbTaskSet, Query, json_stream

from fairways.decorators import entrypoint, use

from fairways.chains import Chain 

from fairways.funcflow import FuncFlow as ff

from fairways.helpers import rows2dict

from fairways.ci import (fakedb, utils)

log = logging.getLogger("cron")

# sched_logger = log

# class AppState:
#     def __init__(self):
#         ticks = 0
    
#     def inc(self):
#         self.tick = 

def start(ctx):
    log.info("Dummy started")
    return {}

def stop(ctx):
    log.info("Dummy -done ")
    return {}

@entrypoint.cron(seconds=10)
def run(ctx):
    log.debug(f"Running @entrypoint.cron...{__name__}")
    return Chain(start).then(stop)

@entrypoint.qa()
def test(ctx):
    log.debug(f"Running @entrypoint.test...{__name__}")
    return Chain(start).then(stop)