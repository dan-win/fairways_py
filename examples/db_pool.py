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

from fairways.io.generic import (
    QueriesSet, 
    SqlQuery)

from fairways.io.syn.sqlite import (
    SqLite,
)


from fairways.decorators import (connection, entrypoint, use)

from fairways.chains import Chain 

from fairways.funcflow import FuncFlow as ff

from fairways.helpers import rows2dict

from fairways.ci import (fakedb, utils)

log = logging.getLogger()


# class AppState:
#     def __init__(self):
#         ticks = 0
    
#     def inc(self):
#         self.tick = 

db_alias = 'db_sqlite_example'

@connection.define()
class TestTaskSet(QueriesSet):

    CREATE_TABLE = SqlQuery(
        """CREATE TABLE fairways (
            id integer primary key,
            name varchar
        );""", 
        db_alias, 
        SqLite,
        ()
    )

    INSERT_DATA = SqlQuery(
        """insert into fairways (id, name) values (1, "My Way");""", 
        db_alias, 
        SqLite,
        ()
    )

    SELECT_DATA = SqlQuery(
        """select name from fairways where id=1;""", 
        db_alias, 
        SqLite,
        ()
    )


def start(ctx):
    log.info("Dummy started")
    return {}


@use.connection('dba')
def create_table(ctx, dba=None):
    dba.CREATE_TABLE.execute()
    return ctx

@use.connection('dba')
def insert_data(ctx, dba=None):
    dba.INSERT_DATA.execute()
    return ctx

@use.connection('dba')
def select_data(ctx, dba=None):
    result = dba.SELECT_DATA.get_records()
    return {"result": result}


def stop(ctx):
    log.info(f"Database operations done: {ctx}")
    return {"result": "ok"}

@entrypoint.cli()
def run(ctx):
    log.debug(f"Running @entrypoint.cron...{__name__}")
    return Chain(start).then(stop)

@entrypoint.qa()
def test(ctx):
    log.debug(f"Running @entrypoint.test...{__name__}")
    return Chain(start).then(stop)

if __name__ == '__main__':
    ctx = {}
    run(ctx)