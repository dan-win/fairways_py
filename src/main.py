import os, sys
from dotenv import load_dotenv

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))

if root_path not in sys.path: 
    sys.path.append(root_path)

env_path = os.path.join(root_path, ".env")
load_dotenv(verbose=True,dotenv_path=env_path)

import logging
logging.basicConfig(
    # filename='example.log', 
    format='%(asctime)s %(levelname)s:%(message)s', 
    level=logging.DEBUG)
log = logging.getLogger(__name__)


import pools.gaecomm as gaecomm


run = gaecomm.run
test_run = gaecomm.test 

if __name__ == "__main__":
    import sys
    from hostapi.io import json_stream

    if len(sys.argv) > 1:
        if sys.argv[1] == '--task' and len(sys.argv) > 2:
            taskname = sys.argv[2]
            method = getattr(gaecomm, taskname)
            if callable(method):
                print("Running single task: '{}'".format(taskname))
                method({})

        elif sys.argv[1] == '--fake' and len(sys.argv) == 2:
            print("Test mode...")

            test_run().then(            
                json_stream('./result100.json')
            )

        else:
            print("Usage: {} --task <func_name>".format(sys.argv[0]))
    
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