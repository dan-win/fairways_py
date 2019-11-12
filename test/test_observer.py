import unittest


import json
import os

from fairways import conf
from fairways import log

import logging


def setUpModule():
    pass

def tearDownModule():
    pass


@unittest.skip("WIP")
class StateShapeExplorerTestCase(unittest.TestCase):

    def test_shape_explores(self):
        from fairways import taskflow
        from fairways.ci.observer import StateShapeExplorer
        from fairways.decorators import entrypoint

        import pprint

        def task1(data):
            "doc 1"
            return data

        def task2(data):
            "doc 2"
            return data

        def task3(data):
            "doc 3"
            return data

        def task4(data):
            "doc 4"
            return data

        def catch_some(data):
            "doc 5"
            print("ERROR: catch_some: ", data)
            return data

        def catch_all(data):
            "doc 6"
            print("ERROR: catch_all: ", data)
            return data

        chain = taskflow.Chain("Main").then(
            task1
            ).on("event", task2
            ).then(task3
            ).then(task4
            ).catch_on(TypeError, catch_some
            ).catch(catch_all)

        explorer = StateShapeExplorer(chain)
        # result = chain({}, middleware=middleware)

        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(explorer.walk())
    
from test.test_env import SKIP_EXT_DB_SERVERS
@unittest.skipIf(SKIP_EXT_DB_SERVERS, 
    "Skip when test servers are not available in environment")
class ObserverTestCase(unittest.TestCase):

    def test_observer(self):
        from fairways import taskflow
        from fairways.ci.observer import ObserverMiddleware
        from fairways.ci.influx_observer import InfluxReflectorMiddleware
        from fairways.decorators import entrypoint

        import pprint

        def task1(data):
            "doc 1"
            return data

        def task2(data):
            "doc 2"
            return data

        def task3(data):
            "doc 3"
            return data

        def task4(data):
            "doc 4"
            return data

        def catch_some(data):
            "doc 5"
            print("ERROR: catch_some: ", data)
            return data

        def catch_all(data):
            "doc 6"
            print("ERROR: catch_all: ", data)
            return data

        chain = taskflow.Chain("Main").then(
            task1
            ).on("event", task2
            ).then(task3
            ).then(task4
            ).catch_on(TypeError, catch_some
            ).catch(catch_all)
        
        # middleware = ObserverMiddleware(chain)
        middleware = InfluxReflectorMiddleware(chain)
        result = chain({}, middleware=middleware)

        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(explorer.walk())