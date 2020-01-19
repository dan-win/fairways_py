# -*- coding: utf-8 -*-
"""
Updates catalog in easyrec
"""
import os, sys

if "./.." not in sys.path:
    sys.path.append("./..")

import logging

log = logging.getLogger(__name__)

import re
import json
import csv
import itertools

import requests
import urllib

from enum import Enum, IntEnum

# import fairways

from fairways.io.generic import (
    QueriesSet, 
    SqlQuery)

from fairways.io.syn.sqlite import (
    SqLite,
)


from fairways.decorators import (connection, entrypoint, use)

from fairways.taskflow import Chain 

from fairways.funcflow import FuncFlow as ff

from fairways.helpers import rows2dict

from fairways.ci import (fakedb, utils)

log = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

db_alias = 'db_sqlite_example'
os.environ[db_alias] = ":memory:"

@connection.define()
class ExampleQueriesSet(QueriesSet):

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
    result = dba.CREATE_TABLE.execute()
    return ctx

@use.connection('dba')
def insert_data(ctx, dba=None):
    dba.INSERT_DATA.execute()
    return ctx

@use.connection('dba')
def select_data(ctx, dba=None):
    result = dba.SELECT_DATA.get_records()
    return {"records": result}

def handle_error(err_info):
    log.error("ERROR: %r", err_info)

def stop(ctx):
    log.info("Database operations done: %s", ctx)
    ctx.update({"result": "ok"})
    return ctx

chain = Chain("DB example").then(
        create_table
    ).then(
        insert_data
    ).then(
        select_data
    ).then(
        stop
    ).catch(
        handle_error
    )

@entrypoint.cmd(param='run')
def run(ctx):
    log.debug(f"Running @entrypoint.cmd...{__name__}")
    result = chain({})
    log.info("Result: %s", result)

@entrypoint.qa()
def test(ctx):
    log.debug(f"Running @entrypoint.test...{__name__}")
    return Chain(start).then(stop)

if __name__ == '__main__':
    ctx = {}
    entrypoint.cmd.run()