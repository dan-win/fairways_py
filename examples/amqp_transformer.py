# -*- coding: utf-8 -*-
"""Example: AMQP transformer (consume->transform->publish)
"""
import sys

if "./.." not in sys.path:
    sys.path.append("./..")

from fairways import conf
from fairways import log
import logging
log = logging.getLogger()
log.setLevel(level=logging.DEBUG)

from fairways.io.asyn import amqp
from fairways.taskflow import Chain 
from fairways.funcflow import FuncFlow as ff
from fairways.io.asyn.base import run_asyn

def fetch_message(raw):
    print(f"Step1 ctx: {type(raw)} | {raw.body}")
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
    # failure = err_info
    extype, failure = err_info.popitem()
    print("ERROR: Something wrong!", repr(failure))


chain = Chain("AMQP transformer"
    ).then(
        fetch_message
    ).then(
        transform_message
    ).then(
        relay_message
    ).then(
        check_pub_result
    ).catch(
        handle_error
    )

@amqp.consumer(queue="fairways")
def run(message):
    return chain(message)

if __name__ == '__main__':
    # run_asyn([
    #     amqp.consumer.create_tasks_future(), 
    #     amqp.producer.create_tasks_future()
    # ])

    import asyncio

    loop = asyncio.get_event_loop()
    tasks = asyncio.gather(*[
        amqp.consumer.create_tasks_future(), 
        amqp.producer.create_tasks_future()
    ], loop=loop)
    loop.run_until_complete(tasks)
