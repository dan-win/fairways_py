# -*- coding: utf-8 -*-
import os, sys
from dotenv import load_dotenv

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))

def append_path(path):
    if path not in sys.path: 
        sys.path.append(path)

append_path(root_path)

# pools_path = os.path.join(root_path, ".env")

env_path = os.path.join(root_path, ".env")
load_dotenv(verbose=True,dotenv_path=env_path)

import logging

LOG_LEVEL = {
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}[
    os.getenv("LOG_LEVEL", "DEBUG")
]

logging.basicConfig(
    # filename='example.log', 
    format='%(asctime)s %(levelname)s:%(message)s', 
    level=LOG_LEVEL)
log = logging.getLogger(__name__)

import pkgutil, importlib

# import pools.gaecomm as gaecomm
import pools

package=pools
for importer, modname, ispkg in pkgutil.walk_packages(path=package.__path__,
                                                      prefix=package.__name__+'.',
                                                      onerror=lambda x: None):
    if ispkg:
        print("print package name", modname)

    else:
        print("print module name", modname)


    print(">>>>>>>>", modname)
    importlib.import_module(modname, package=None)    



# run = gaecomm.run
# test_run = gaecomm.test 

if __name__ == "__main__":
    import sys
    import json
    from hostapi.io import json_stream

    if len(sys.argv) > 3:

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

        elif sys.argv[1] == '--fake' and len(sys.argv) == 2:
            print("Test mode...")

            test_run().then(            
                json_stream('./result100.json')
            )

        else:
            print("Usage: {} --pool <poolname> --task <func_name> ['optional ctx arg in json string']".format(sys.argv[0]))
    
    else:
        import schedule
        import time
        def job():
            run()
        
        schedule.every(30).seconds.do(job)

        # Run forst iteration immediately
        job()
        while True:
            schedule.run_pending()
            time.sleep(1)