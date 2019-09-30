import asyncio
import concurrent.futures
import functools

### Start chain as ordinary non-blocking function! 

def io_task(func):
    """Whap "async" function / coroutine

    Arguments:
        func {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        local_loop = None
        try:
            loop = asyncio.get_event_loop()
        except Exception as e:
            print("LOOP ERROR:", e)
            # Handle case when task lauched from TreadPoolExecutor wihtout running loop:
            local_loop = loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        try:
            task = asyncio.ensure_future(func(*args, **kwargs), loop=loop)
            # Note that "gather" wraps results into list:
            (result,) = loop.run_until_complete(asyncio.gather(task))
            return result
        finally:
            if local_loop:
                local_loop.close()
    return wrapper

def cpu_task(func):
    """Wrap syncronous (ordinary) function which relates to cpu-bound operations
    
    Arguments:
        func {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func, *args, **kwargs)
            #Note that future.result() can throw exception which implicitly propagated to upper level, this is desired behaviour
            return future.result()

    return wrapper