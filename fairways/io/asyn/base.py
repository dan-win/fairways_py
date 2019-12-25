from fairways.io.generic import (DataDriver, UriConnMixin, FileConnMixin)

import asyncio

import logging

log = logging.getLogger()

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

    async def _output_stream(self, message):
        """
        This method should be redefined in descendants. 
        This sample is for demo purposes only"""
        # print('relaying {}'.format(message))
        print(f'{str(self)} relaying {message}')

    async def _shutdown(self, sig):
        print(f'\nCaught {sig.name}')
        # print(f'Shutting down {str(self)} ...')
        # stop_event.set()
        self.STOP_EVENT.set()
        print('Stop event set!...')
        await asyncio.sleep(1)
    
    async def process_input(self, queue):
        """
        Produce message to internal queue. 
        Note that this method can act as a consumer for external source!
        * Final method *
        """
        
        async for message in self._input_stream():
            await queue.put(message)
            await asyncio.sleep(random.random())
            # if stop_event.is_set():
            if self.STOP_EVENT.is_set():
                print(f'Stopping producer for {str(self)}')
                await queue.put(self.SENTINEL)
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
                s, lambda: asyncio.ensure_future(self._shutdown(s)))

        # schedule the consumer
        consumer = asyncio.ensure_future(self.process_output(queue))
        # run the producer and wait for completion
        await self.process_input(queue)
        # wait until the consumer has processed all items
        await queue.join()
        # the consumer is still awaiting for an item, cancel it
        consumer.cancel()

    def __init__(self):
        self.id = uuid.uuid4()
    
    def __str__(self):
        return f'Loop {self.id.hex}'