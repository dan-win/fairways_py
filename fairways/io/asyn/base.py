from fairways.io.generic import (DataDriver, UriConnMixin, FileConnMixin)

import asyncio
import concurrent
import logging

log = logging.getLogger(__name__)

class AsyncDataDriver(DataDriver):

    async def _ensure_connection(self):
        if self.is_connected():
            return
        log.warning("Restoring DB connection: {}".format(self.db_name))
        await self._connect()

    async def _connect(self):
        raise NotImplementedError(f"Override _connect for {self.__class__.__name__}")
    
    async def close(self):
        if self.is_connected():
            await self.engine.close()
            self.engine = None

    def _setup_cursor(self, cursor):
        return cursor

    async def fetch(self, sql):
        try:
            await self._ensure_connection()
            async with self.engine.cursor() as cursor:
                await cursor.execute(sql)
                cursor = self._setup_cursor(cursor)
                return await cursor.fetchall()
        except Exception as e:
            log.error("DB operation error: {} at {}".format(e, self.db_name))
            raise
        finally:
            if self.autoclose:
                await self.close()

    async def change(self, sql):
        try:
            await self._ensure_connection()
            async with self.engine.cursor() as cursor:
                await cursor.execute(sql)
            await self.engine.commit()
        except Exception as e:
            log.error("DB operation error: {} at {}; {}".format(e, self.db_name, sql))
            raise
        finally:
            if self.autoclose:
                await self.close()

    # Inherited (note: sync method, acts as a proxy to coroutine):
    # def get_records(self, query_template, **params):

    # Inherited:
    # def execute(self, query_template, **params):



import random
import signal
import uuid

from contextlib import suppress

class AsyncLoop:
    
    # __slots__ = ["loop"]

    STOP_ON_SIGNALS = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)

    SENTINEL = "None"

    STOP_EVENT = asyncio.Event()

    def _create_queue(self, loop):
        return asyncio.Queue(loop=loop)
    
    async def _input_stream(self):
        """
        This method should be redefined in descendants. 
        This sample is for demo purposes only"""
        for x in range(1, 10):
            # produce an item
            print(f'{str(self)} producing {x}')
            # simulate i/o operation using sleep
            yield str(x)
            await asyncio.sleep(random.random())
        yield self.SENTINEL
        await asyncio.sleep(random.random())
    
    # async def _input_adapter(self):

    async def process_interruption(self):
        print('waiting for it ...')
        await self.STOP_EVENT.wait()
        print('STOP EVENT detected!')

    async def _output_stream(self, message):
        """
        This method should be redefined in descendants. 
        This sample is for demo purposes only"""
        # print('relaying {}'.format(message))
        print(f'{str(self)} relaying message')

    async def _shutdown(self, sig):
        print(f'\nCaught {sig.name}')
        # print(f'Shutting down {str(self)} ...')
        # stop_event.set()
        # await queue.put(self.SENTINEL)
        self.STOP_EVENT.set()
        print('Stop event set!...')
        await asyncio.sleep(1)
    
    async def process_input(self, queue):
        """
        Produce message to internal queue. 
        Note that this method can act as a consumer for external source!
        * Final method *
        """
        # sel = selectors.DefaultSelector()
        # sel.register(self.STOP_EVENT)
        # sel.register(self._input_stream)

        async for message in self._input_stream():
        # async for message in sel.select():
            # print("Message is: ", message)
            await queue.put(message)
            await asyncio.sleep(random.random())
            # if stop_event.is_set():
            if message == self.SENTINEL:
                print(f'Stopping producer for {str(self)}')
                # await queue.put(self.SENTINEL)
                break
            if self.STOP_EVENT.is_set():
                print(f'Stopping producer for {str(self)}')
                # await queue.put(self.SENTINEL)
                break

    async def process_output(self, queue):
        """
        Consume message from internal queue. 
        Note that this method can act as a producer for external destination!
        * Final method *
        """

        while True:
            # wait for an item from the producer
            item = await queue.get()
            if item == self.SENTINEL:
                # the producer emits None to indicate that it is done
                print("Process output - SENTINEL found, exiting")
                queue.task_done()
                # self.STOP_EVENT.set()
                break
            
            print("Output stream [entering]")
            # process the item
            await self._output_stream(item)

            print("Output stream [done]")

            # Notify the queue that the item has been processed
            queue.task_done()
            print("Queue task [done]")

    async def run(self, loop):
        """ Create main loop as async task """

        print(f"Starting {str(self)}")
        queue = self._create_queue(loop)

        signals = self.STOP_ON_SIGNALS
        for s in signals:
            loop.add_signal_handler(
                s, lambda: asyncio.ensure_future(self._shutdown(s), loop=loop))

        # schedule the consumer
        consumer = asyncio.ensure_future(self.process_output(queue), loop=loop)

        # schedule producer along with stop listener
        tasks = [
            self.process_interruption(), 
            self.process_input(queue)
        ]

        finished, unfinished = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED, loop=loop)
        # await self.process_input(queue)

        for task in unfinished:
            await close_task(task)

        # await asyncio.wait(unfinished)

        # wait until the consumer has processed all items
        await queue.join()

        # the consumer is still awaiting for an item, cancel it
        close_task(consumer)

    def __init__(self):
        self.id = uuid.uuid4()
    
    def __str__(self):
        return f'Aio Loop {self.id.hex}'


async def close_task(task):
    task.cancel()
    with suppress(asyncio.CancelledError, concurrent.futures.CancelledError):
        print('Closing unfinished task', task)
        await task
    log.debug("Task closed: %s", task)


class AsyncEndpoint:
    """Base class to build endpoint decorators (both consumers and producers).
    Contains internal management for async loops    
    """

    @classmethod
    def driver_factory(cls, args=None):
        "Should return driver instance (or connection pool instance)"
        raise NotImplementedError()

    @classmethod
    def wrap_taskflow_item(cls, driver, entrypoint_item):
        "Should return instance of AsyncLoop "
        raise NotImplementedError()

    @classmethod
    def create_tasks_future(cls, driver, args=None):
        "Returns awaitable"
        items_to_run = cls.items()
        if not items_to_run:
            raise ValueError("Cannot find amqp entrypoints")

        # driver = cls.driver_factory(args)
        
        loop = asyncio.get_event_loop()

        # Note that "gather" wraps results into list:
        tasks_future = asyncio.gather(*[
            # run_consumer(driver, item)
            cls.wrap_taskflow_item(driver, item, loop).run(loop)
            for item in items_to_run
        ], loop=loop)

        return tasks_future

    @classmethod
    def run(cls, args=None):

        # items_to_run = cls.items()
        # if not items_to_run:
        #     raise ValueError("Cannot find amqp entrypoints")

        driver = cls.driver_factory(args)
        
        loop = asyncio.get_event_loop()

        # # Note that "gather" wraps results into list:
        # tasks_future = asyncio.gather(*[
        #     # run_consumer(driver, item)
        #     cls.wrap_taskflow_item(driver, item, loop).run(loop)
        #     for item in items_to_run
        # ], loop=loop)

        tasks_future = cls.create_tasks_future(driver, args)

        try:
            log.debug("Jumping into loop")
            loop.run_until_complete(tasks_future)
            # return result
            log.debug("Exiting...")
            # Wait for pending tasks:
            pending = asyncio.Task.all_tasks()
            log.debug("Pending: %s", len(pending))
            pending_future = asyncio.gather(*pending)
            loop.run_until_complete(pending_future)
            log.info("Done")

        # except KeyboardInterrupt:  # pragma: no branch
        #     pass
        except asyncio.CancelledError as e:
            log.debug("CancelledError intercepted: %s", e)

        finally:
            log.debug("Closing driver...")
            loop.run_until_complete(driver.close())
            log.debug("Driver closed")
