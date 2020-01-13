import os, sys
import logging
logging.basicConfig( stream=sys.stderr )

try:
    from colorlog import ColoredFormatter
    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)-8s %(message)s%(reset)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red',
        }
    )
except:
    formatter = None
    print("You could install colorlog")

def getLogger():        
    handler = logging.StreamHandler()
    if formatter:
        handler.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(handler)
    return root

def run_asyn(awaitable_obj, destructor=None):
    import asyncio
    import inspect
    import signal

    async def close_task(task):
        task.cancel()
        with suppress(asyncio.CancelledError, concurrent.futures.CancelledError):
            print('Closing unfinished task', task)
            await task
        log.debug("Task closed: %s", task)

    async def shutdown(sig):
        for task in asyncio.Task.all_tasks():
            close_task(task)
        log.debug("Shutdown complete.")

    loop = asyncio.get_event_loop()

    log = getLogger()

    for s in (signal.SIGHUP, signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            s, lambda: asyncio.ensure_future(self._shutdown(s), loop=loop))

    try:
        log.debug("Jumping into loop")
        # Main loop here:
        loop.run_until_complete(awaitable_obj)
        # Main loop done (Ctrl+C, ...), exiting
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

    # own_loop = None
    # if new_loop:
    #     own_loop = asyncio.new_event_loop()
    #     asyncio.set_event_loop(own_loop)
    #     loop = own_loop
    # else:
    #     loop = asyncio.get_event_loop()
    # try:
    #     task = asyncio.ensure_future(coro_obj, loop=loop)
    #     # Note that "gather" wraps results into list:
    #     (result,) = loop.run_until_complete(asyncio.gather(task))
    #     return result
    # finally:
    #     if own_loop:
    #         own_loop.close()
