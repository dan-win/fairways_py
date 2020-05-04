import unittest
import unittest.mock

import fairways

from fairways.ci.utils import csv2py

from fairways.funcflow import FuncFlow as ff
from fairways.decorators.entrypoint import QA

from fairways import conf
from fairways import log

import logging

def setUpModule():
    pass

def tearDownModule():
    pass

class FixtureTestTemplate(unittest.TestCase):
    subject_module = ""
    fixture = {}

    # @classmethod
    def setUp(cls):
        # from ci import fakedb
        # import json
        # import os
        import importlib
        cls.module_to_test = importlib.import_module(cls.subject_module)
        cls.modname = cls.module_to_test.__name__

        from fairways import log
        from fairways.conf import load
        load(None)
        import logging
        log = logging.getLogger()
        cls.log = log

        from fairways.io import generic as io_generic 
        from fairways import decorators
        from fairways.funcflow import FuncFlow as ff
        cls.ff = ff
        cls.io_generic = io_generic
        cls.decorators = decorators
        import unittest.mock

    
    def get_response_with_fixture(self, fixture_dict=None, middleware=None):
        """
        Call this method to run actual test
        """
        ff = self.ff
        decorators = self.decorators
        QueriesSet = self.io_generic.QueriesSet

        entry = ff.find(QA.items(), lambda r: r.module == self.modname)

        self.log.debug("ENTRYPOINT: %s", entry)

        module_conn = decorators.connection.define.find_module_entity(self.modname)
        fixture_name = f"{self.subject_module}_fixture_queries_set".upper()
        fixture_dict = fixture_dict or self.fixture
        fixture_queriesset = QueriesSet.from_fixtures_dict(fixture_name, **fixture_dict)

        with unittest.mock.patch.object(module_conn, "subject", fixture_queriesset):
            ctx = {}
            result = entry.handler(ctx, middleware=middleware)
        
        return result

    def get_response_with_request_fixture(self, fixture_dict=None, middleware=None, test_funcname=None):
        """
        Call this method to run test without mock db
        """
        ff = self.ff
        decorators = self.decorators

        entry = ff.filter(QA.items(), lambda r: r.module == self.modname)

        if len(entry) > 1: 
            if test_funcname is None:
                raise TypeError("Your source module contains more than one test, you should provide 'test_funcname' to select exact test")
            entry = ff.find(entry, lambda r: r.subject.__name__ == test_funcname)
        else:
            entry = entry[0]

        self.log.debug("ENTRYPOINT: %s", entry)

        # module_conn = decorators.connection.define.find_module_entity(self.modname)
        # fixture_name = f"{self.subject_module}_fixture_queries_set".upper()
        fixture_dict = fixture_dict or self.fixture
        # fixture_queriesset = QueriesSet.from_fixtures_dict(fixture_name, **fixture_dict)

        # with unittest.mock.patch.object(module_conn, "subject", fixture_queriesset):
        #     ctx = {}
        result = entry.handler(fixture_dict, middleware=middleware)
        
        return result
