# -*- coding: utf-8 -*-
"""
"""
import os, sys

if "./.." not in sys.path:
    sys.path.append("./..")
# import fairways

from fairways.io.asyn import amqp
from fairways.io.asyn.consumer import amqp as amqp_sub

from fairways.io.asyn.publisher import amqp as amqp_pub

from fairways.decorators import (connection, entrypoint, use)

from fairways.taskflow import Chain 

from fairways.funcflow import FuncFlow as ff

from fairways.ci.helpers import run_asyn

import logging

log = logging.getLogger()
# logging.

def fetch_message(raw):
    print(f"Step1 ctx: {type(raw)} | {raw.body}")
    # format message (further, use ALL fields of aiopika Message?)
    message = dict(
        body=raw.body,
        headers=raw.headers
    )
    return message

def transform_message(message):
    print(f'Step2 ctx: {type(message)} | {message["body"]}')
    body = str(message["body"])
    new_body = f'*** {body} ***'
    return ff.weld(message, dict(body=new_body))

@amqp.producer(exchange="fws-out")
def relay_message(message):
    print(f'Step3 ctx: {type(message)} | {message["body"]}')
    return message

def check_pub_result(result):
    print(f"Step after publish: {type(result)}")
    return result


def handle_error(err_info):
    failure = err_info
    print("ERROR: Something totally wrong!", str(failure)[:1000])
    # return {}


chain = Chain("AMQP transformer"
    ).then(fetch_message
    ).then(transform_message
    ).then(relay_message
    ).then(check_pub_result
    ).catch(handle_error
    )

@amqp.consumer(queue="fairways")
def run(message):
    # print("GOT message:", message)
    return chain(message)

if __name__ == '__main__':
    run_asyn([
        amqp.consumer.create_tasks_future(), 
        amqp.producer.create_tasks_future()
    ])

