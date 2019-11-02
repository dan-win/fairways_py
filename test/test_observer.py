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


class ObserverTestCase(unittest.TestCase):

    def test_observer(self):
        from fairways import taskflow
        from fairways.ci.observer import StateShapeExplorer
        from fairways.decorators import entrypoint

        import pprint

        def task1(data):
            return data

        def task2(data):
            return data

        def task3(data):
            return data

        def catch_some(data):
            return data

        def catch_all(data):
            return data

        chain = taskflow.Chain("Main").then(
            task1
            ).on("event", task2
            ).then(task3
            ).catch_on(TypeError, catch_some
            ).catch(catch_all)

        explorer = StateShapeExplorer(chain)
        # result = chain({}, middleware=middleware)

        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(explorer.walk())