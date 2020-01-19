Module io.asyn.amqp
======================

Asyncronous AMQP/RabbitMQ driver.

Example app using async.amqp module:
------------------------------------

.. code-block:: python
   :linenos:

    # Naive use case, demo only

    from fairways.taskflow import Chain 
    from fairways.funcflow import FuncFlow as ff
    from fairways.decorators import (connection, entrypoint, use)
    from fairways.io.asyn import amqp
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

    # Result of this function will be automatically 
    # published to selected exchange.
    # Do not forget to run publisher loop later
    # with `amqp.producer.create_tasks_future`.
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
        return {}

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

    # Mark function as consumer handler.
    # Consider it as a main entrypoint in this app.
    # Run it later with `amqp.consumer.create_tasks_future`
    @amqp.consumer(queue="fairways")
    def run(message):
        # We starting our lazy chain
        # each time when incoming message occurs
        return chain(message)

    if __name__ == '__main__':
        run_asyn([
            # Here is we firing loop for all consumers in app:
            amqp.consumer.create_tasks_future(), 
            # Here is we firing loop for all producers in app:
            amqp.producer.create_tasks_future()
        ])


Module content
--------------

.. automodule:: fairways.io.asyn.amqp
   :members:
