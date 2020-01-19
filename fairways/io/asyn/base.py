from fairways.io.generic import (DataDriver, UriConnMixin, FileConnMixin)

import asyncio
import concurrent
from abc import abstractmethod

import logging
log = logging.getLogger(__name__)

class AsyncDataDriver(DataDriver):
    """Base for async drivers.
    
    :param env_varname: Name of enviromnent variable (or settings attribute) which holds connection string (e.g.: "mysql://user@pass@host/db")
    :type env_varname: str
    """

    async def _ensure_connection(self):
        if self.is_connected():
            return
        log.warning("Connecting resource: {}".format(self.db_name))
        await self._connect()

    @abstractmethod
    async def _connect(self):
        "Should be overriden in descendants"
        raise NotImplementedError(f"Override _connect for {self.__class__.__name__}")
    
    async def close(self):
        """Close connection if alive.
        * Final *
        """
        if self.is_connected():
            await self.engine.close()
            self.engine = None

    def _setup_cursor(self, cursor):
        return cursor

    async def fetch(self, query_script):
        """Fetch data from resource
        
        :param query_script: Script to fetch data (SQL for databases)
        :type query_script: Any
        :return: Awaitable wich resolves to result (list or records)
        :rtype: Awaitable
        """
        try:
            await self._ensure_connection()
            async with self.engine.cursor() as cursor:
                await cursor.execute(query_script)
                cursor = self._setup_cursor(cursor)
                return await cursor.fetchall()
        except Exception as e:
            log.error("Resource operation error: %r at %s", e, self.db_name)
            raise
        finally:
            if self.autoclose:
                await self.close()

    async def change(self, query_script):
        """Change data on resource
        
        :param query_script: Script to fetch data (SQL for databases)
        :type query_script: Any
        """
        try:
            await self._ensure_connection()
            async with self.engine.cursor() as cursor:
                await cursor.execute(query_script)
            await self.engine.commit()
        except Exception as e:
            log.error("Resource operation error: {} at {}; {}".format(e, self.db_name, query_script))
            raise
        finally:
            if self.autoclose:
                await self.close()


import random
import signal
import uuid

from contextlib import suppress

class AsyncLoop:
    """Async loop for message processing.
    You can run multiple instances of such loop at the same time.
    Clean shutdown on system signals. 
    """
    
    # __slots__ = ["loop"]

    STOP_ON_SIGNALS = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)

    SENTINEL = "None"

    STOP_EVENT = asyncio.Event()

    def _create_queue(self, loop):
        return asyncio.Queue(loop=loop)
    
    @abstractmethod
    async def input_stream(self):
        """This method should be redefined in descendants. 
        This implementation is for demo purposes only
        
        :yield: Incoming message
        :rtype: Any
        """
        for x in range(1, 10):
            # produce an item
            print(f'{str(self)} producing {x}')
            # simulate i/o operation using sleep
            yield str(x)
            await asyncio.sleep(random.random())
        yield self.SENTINEL
        await asyncio.sleep(random.random())

    @abstractmethod
    async def output_stream(self, message):
        """This method should be redefined in descendants. 
        This implementation (see source) is for demo purposes only
        
        :param message: Outgoing message after processing
        :type message: Any
        """
        print(f'{str(self)} relaying message')

    async def process_interruption(self):
        """Waiting for STOP_EVENT
        """
        log.debug('Listening for STOP_EVENT ...')
        await self.STOP_EVENT.wait()
        log.debug('STOP EVENT detected!')

    async def _shutdown(self, sig):
        log.debug('Caught %s', sig.name)
        # print(f'Shutting down {str(self)} ...')
        # stop_event.set()
        # await queue.put(self.SENTINEL)
        self.STOP_EVENT.set()
        log.debug('Stop event set!...')
        await asyncio.sleep(1)
    
    async def process_input(self, queue: asyncio.Queue):
        """Publish incoming message into internal queue. 
        Note that this method can act as a consumer for external source!
        * Final method *
        
        :param queue: Internal queue to put incoming message into
        :type queue: asyncio.Queue
        """

        async for message in self.input_stream():
        # async for message in sel.select():
            # print("Message is: ", message)
            await queue.put(message)
            await asyncio.sleep(random.random())
            # if stop_event.is_set():
            if message == self.SENTINEL:
                log.debug('Stopping producer for %s', self)
                # await queue.put(self.SENTINEL)
                break
            if self.STOP_EVENT.is_set():
                log.debug('Stopping producer for %s', self)
                # await queue.put(self.SENTINEL)
                break

    async def process_output(self, queue:asyncio.Queue):
        """Consume message from internal queue. 
        Note that this method can act as a producer for external destination!
        * Final method *
        
        :param queue: Internal queue which receives incoming messages
        :type queue: asyncio.Queue
        """

        while True:
            # wait for an item from the producer
            item = await queue.get()
            if item == self.SENTINEL:
                # the producer emits None to indicate that it is done
                log.debug("Process output - SENTINEL found, exiting")
                queue.task_done()
                # self.STOP_EVENT.set()
                break
            
            log.debug("Output stream [entering]")
            # process the item
            await self.output_stream(item)

            log.debug("Output stream [done]")

            # Notify the queue that the item has been processed
            queue.task_done()
            log.debug("Queue task [done]")

    async def run(self, loop):
        """ Create main loop as async task """

        log.info("Starting %s", self)
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
        """Constructor method
        """
        self.id = uuid.uuid4()
    
    def __str__(self):
        return f'Aio Loop {self.id.hex}'


async def close_task(task):
    task.cancel()
    with suppress(asyncio.CancelledError, concurrent.futures.CancelledError):
        log.debug('Closing unfinished task: %s', task)
        await task
    log.debug("Task closed: %s", task)


class AsyncEndpoint:
    """Base class to build endpoint decorators (both consumers and producers).
    Contains internal management for async loops    
    """

    @classmethod
    @abstractmethod
    def driver_factory(cls, args=None) -> AsyncDataDriver:
        """Should return driver instance (or connection pool instance).
        
        :param args: Arguments for driver factory, defaults to None
        :type args: Any, optional
        :return: Driver instance
        :rtype: AsyncDataDriver
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def wrap_taskflow_item(cls, driver, entrypoint_item):
        "Should return instance of AsyncLoop "
        raise NotImplementedError()

    @classmethod
    def create_tasks_future(cls, args=None):
        """Wrap all endpoint processes into a asyncio.Future.
        This is recommended way to run multiple types of endpoints at the same time 
        (gather futures and pass them into run_asyn) 
        
        :param args: Args for driver factory, defaults to None
        :type args: Any, optional
        :raises ValueError: No endpoints, nothing to run
        :return: Single future which wraps all underlying tasks
        :rtype: asyncio.Future
        """
        items_to_run = cls.items()
        if not items_to_run:
            raise ValueError("Cannot find async entrypoints")

        driver = cls.driver_factory(args)
        
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
        """Run all registered endpoints.
        Blocking function.
        
        :param args: Args for underlying driver, defaults to None
        :type args: Any, optional
        """

        tasks_future = cls.create_tasks_future(args)
        run_asyn(tasks_future)

def run_asyn(awaitable_obj, destructor=None):
    """Manager to run awaitables (futures, tasks).
    Clean shutdown on system signals.
    Blocking function.
    
    :param awaitable_obj: Task or list of tasks to run together.
    :type awaitable_obj: Awaitable or list[Awaitable]
    :param destructor: Destructor function without parameters, defaults to None
    :type destructor: Awaitable or Callable, optional
    """
    import asyncio
    import inspect
    import signal

    async def close_task(task):
        task.cancel()
        with suppress(asyncio.CancelledError, concurrent.futures.CancelledError):
            log.info('Closing unfinished task: %s', task)
            await task
        log.debug("Task closed: %s", task)

    async def shutdown(sig):
        for task in asyncio.Task.all_tasks():
            close_task(task)
        log.debug("Shutdown complete.")

    loop = asyncio.get_event_loop()

    for s in (signal.SIGHUP, signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            s, lambda: asyncio.ensure_future(self._shutdown(s), loop=loop))

    try:
        log.debug("Jumping into loop")
        # Main loop here:
        if isinstance(awaitable_obj, (list, tuple)):
            tasks = list(awaitable_obj)
        else:
            tasks = [awaitable_obj]
        tasks = [asyncio.ensure_future(t) for t in tasks]
        task = asyncio.gather(*tasks)
        
        loop.run_until_complete(task)
        # Main loop done (Ctrl+C, ...), exiting
        log.debug("Exiting...")
        # Wait for pending tasks:
        pending = asyncio.Task.all_tasks()
        log.debug("Pending: %s", len(pending))
        pending_future = asyncio.gather(*pending, loop=loop)
        loop.run_until_complete(pending_future)
        log.info("Done")

    # except KeyboardInterrupt:  # pragma: no branch
    #     pass
    except asyncio.CancelledError as e:
        log.debug("CancelledError intercepted: %s", e)

    finally:
        log.debug("Closing loop...")
        if callable(destructor):
            d = destructor()
            if inspect.isawaitable(d):
                loop.run_until_complete(d)
                log.debug("Closing with async destructor")
            else:
                log.debug("Closing with sync destructor")
        else:
            log.debug("Closing without destructor")
