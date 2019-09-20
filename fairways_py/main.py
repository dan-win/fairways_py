# -*- coding: utf-8 -*-
import os, sys
from dotenv import load_dotenv
# import pathspec

# import asyncio
# import concurrent.futures
# import multiprocessing

# root_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))

# def append_path(path):
#     if path not in sys.path: 
#         sys.path.append(path)

# append_path(root_path)

# append_path(os.path.join(root_path, "api"))

# pools_path = os.path.join(root_path, ".env")

env_path = os.path.join(root_path, ".env")
load_dotenv(verbose=True,dotenv_path=env_path)

SETTINGS_MODULE = os.environ.get("PYWATERS_SETTINGS_MODULE")
if SETTINGS_MODULE is None:
    SETTINGS_MODULE = "pools.settings"
    os.environ["PYWATERS_SETTINGS_MODULE"] = SETTINGS_MODULE

POOLS_PACKAGE = ".".join(SETTINGS_MODULE.split('.')[:-1])

# import logging

# LOG_LEVEL = {
#     "ERROR": logging.ERROR,
#     "WARNING": logging.WARNING,
#     "INFO": logging.INFO,
#     "DEBUG": logging.DEBUG,
# }[
#     os.getenv("LOG_LEVEL", "DEBUG")
# ]

# logging.basicConfig(
#     # filename='example.log', 
#     format='core: %(asctime)s %(levelname)s:%(message)s', 
#     level=LOG_LEVEL)
# log = logging.getLogger(__name__)


import api

print(f">>>> api: {dir(api)}")


from api import dynload
from api import log
from api.conf import settings

from api.underscore import Underscore as _
from api.decorators.entrypoint import Channel

import logging

log = logging.getLogger(__name__)
    

# import pkgutil, importlib, fnmatch

# # import pools.gaecomm as gaecomm
# import pools

# from api import (core, triggers)





# ignore = None

# try:
#     poolsignore_filepath = os.path.join(root_path, "pools", ".poolsignore")
#     if os.path.isfile(poolsignore_filepath):
#         log.debug(".poolsignore found, processing")
#         with open(poolsignore_filepath, "r") as f:
#             ignore = pathspec.PathSpec.from_lines(
#                 pathspec.patterns.GitWildMatchPattern, 
#                 [line for line in f])
# except Exception as e:
#     log.error(".poolsignore error: %s", e)
#     pass

# package=pools
# imported_names = []
# for importer, modname, ispkg in pkgutil.walk_packages(path=package.__path__,
#                                                       prefix=package.__name__+'.',
#                                                       onerror=lambda x: None):
#     try:
#         if ignore and ignore.match_file(modname):
#             log.debug("Skipping file: %s", modname)
#             continue
        
#         importlib.import_module(modname, package=None)
#         imported_names.append(modname)

#         # # Check registry
#         # if core.registry.cron.get(modname):
#         #     log.info("module '%s' - cron entrypoint found", modname)
#         # else:
#         #     log.warning("module '%s' has no cron entrypoint!", modname)

#     except Exception as e:
#         log.error("Error in module [{}]: {!r}", modname, e)
    
# log.info("Polls imported: %s", imported_names)


# run = gaecomm.run
# test_run = gaecomm.test 

if __name__ == "__main__":
    import sys
    import argparse
    import json
    # from api.io import json_stream

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pool', type=str, default=None, help="Run selected pool only (where name of a pool is a module name where pool is defined)")
    parser.add_argument('-d', '--data', type=str, default=None, help="Initial data for a pool in json format (ignored if no --pool specified)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-t', '--task', type=str, default=None, help="Run selected task only (ignored if no --pool specified)")
    group.add_argument('-e', '--entrypoint', type=str, default="test", choices=("cron", "amqp", "test", "cmd"), help="Selected entrypoint of a pool (ignored if no --pool specified)")
    # --dry-run option
    
    args = parser.parse_args()

    ctx = json.loads(args.data or "{}")

    if args.pool:
        poolname = args.pool
        taskname = args.task
        entrypoint = args.entrypoint

        dynload.import_module(poolname)
        log.info("Pool imported: %s", poolname)
        pool = sys.modules[poolname]

        if entrypoint:
            e = _.filter(Channel.items(), lambda r: r.channel_tag == entrypoint and r.module == poolname)
            # e = triggers.enum_module_triggers(poolname, tag=entrypoint)
            if e is None:
                raise KeyError("Module {} has no entypoint with type {}".format(poolname, entrypoint))
            method = e["method_"]
        else:
            method = getattr(pool, taskname, None)
            if method is None:
                raise KeyError("Module {} has no task {}".format(poolname, taskname))
        print("Running single task: '{}' from pool: '{}'".format(taskname, poolname))
        method(ctx)

    else:
        # Import all:
        imported_names = []
        for mod_name in settings.INSTALLED_APPS:
            mod_qname = f"{POOLS_PACKAGE}.{mod_name}"
            dynload.import_module(mod_qname)
            imported_names += [mod_qname]

        log.info("Pools imported: %s", imported_names)

        entrypoint = args.entrypoint or "cli"

        entrypoints = _.filter(Channel.items(), lambda e: e.channel_tag == entrypoint)

        log.info(f"Running {len(entrypoints)} triggers")

        for handler in _.map(entrypoints, lambda e: e.handler):
            handler(ctx)

        # from api.gateway import run
        # run()
        # import svc 
        # svc.run()

        # from api.asgi_stub import run as asgi_run
        # from api.cron_stub import run as cron_run
        # print("Starting...")
        # # run()

        # # def blocking_function():
        # #     while True:
        # #         schedule.run_pending()
        # #         time.sleep(1)    
        # async def run_blocking_tasks(executor):
        #     loop = asyncio.get_event_loop()
        #     blocking_tasks = [
        #         loop.run_in_executor(executor, cron_run),
        #         loop.run_in_executor(executor, asgi_run),
        #     ]
        #     log.info('waiting for executor tasks')
        #     completed, pending = await asyncio.wait(blocking_tasks)
        #     log.info(f'results: completed:{completed}, pending:{pending}')
        #     log.info('exiting')

        # pool = concurrent.futures.ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()-1)

        # event_loop = asyncio.get_event_loop()
        # try:
        #     event_loop.run_until_complete(
        #         run_blocking_tasks(pool)
        #     )
        # finally:
        #     event_loop.close()



    exit(0)



    # Refactor this part. Looks ugly.
    if len(sys.argv) > 1:

        if sys.argv[1] == '--pool' and sys.argv[3] == '--task' and len(sys.argv) > 3:
            poolname = sys.argv[2]
            taskname = sys.argv[4]
            if len(sys.argv) > 5:
                ctx_str = sys.argv[5]
                ctx = json.loads(ctx_str)
            else:
                ctx = {}
            print ("*****\n", dir (pools), "*****\n")
            pool = getattr(pools, poolname)
            method = getattr(pool, taskname)
            if callable(method):
                print("Running single task: '{}' from pool: '{}'".format(taskname, poolname))
                method(ctx)

        else:
            print("Usage: {} --pool <poolname> --task <func_name> ['optional ctx arg in json string']".format(sys.argv[0]))
    
    else:
        triggers.init()
        # import schedule
        # import time
        # sched_logger = logging.getLogger('schedule')
        # # sched_logger.setLevel(logging.ERROR)
        # tasks = []

        # def job_factory(main_method, poolname):
        #     def job():
        #         try:
        #             main_method(None)
        #         except Exception as e:
        #             log.error("Runtime error in {} cron entrypoint: {!r}".format(poolname, e))
        #     return job

        # for poolname, cron_conf in core.registry.cron.items():
        #     log.info("CRON for %s", poolname)
        #     main_method = cron_conf["method"]
        #     interval_secs = cron_conf.get("seconds")
        #     job = job_factory(main_method, poolname)
        #     # Run forst iteration immediately
        #     job()
        #     # Schedule further executions:
        #     schedule.every(interval_secs).seconds.do(job)

        # # for poolname in known_modules:
        # #     method_name = "run"
        # #     interval_name = "interval_secs"
        # #     pool = getattr(pools, poolname)
        # #     main_method = getattr(pool, method_name, None)
        # #     if main_method is None:
        # #         log.error("Pool {} has no 'run' method!".format(poolname))
        # #         continue # Bypass invalid pool
        # #     interval_secs = getattr(pool, interval_name, None)
        # #     if interval_secs is None:
        # #         log.error("Pool {} has no 'interval_secs' attribute!".format(poolname))
        # #         continue # Bypass invalid pool
        # #     if callable(main_method):
        # #         log.debug("runner: scheduling task sequence: {}.{}".format(poolname, "run"))
        # #         tasks.append((main_method, poolname, method_name, interval_secs))

        # # for (main_method, poolname, method_name, interval_secs) in tasks:
        # #     job = job_factory(main_method, poolname, method_name)
        # #     # Run forst iteration immediately
        # #     job()
        # #     # Schedule further executions:
        # #     schedule.every(interval_secs).seconds.do(job)

        # # def job():
        # #     for (main_method, poolname, method_name, interval_secs) in tasks:
        # #         try:
        # #             main_method(None)
        # #         except Exception as e:
        # #             log.error("Runtime error in {}.{}: {!r}".format(poolname, method_name, e))
            
        #     # poolname = "gaecomm"
        #     # taskname = "run"
        #     # pool = getattr(pools, poolname)
        #     # method = getattr(pool, taskname)
        #     # method()
        
        # # schedule.every(60).seconds.do(job)

        # # Run forst iteration immediately
        # # job()
        # while True:
        #     schedule.run_pending()
        #     time.sleep(1)