import unittest
import unittest.mock

import fairways

from fairways.ci.utils import csv2py

from fairways.funcflow import FuncFlow as ff
from fairways.decorators.entrypoint import Channel

def setUpModule():
    pass

def tearDownModule():
    pass

class FixtureTestTemplate(unittest.TestCase):
    subject_module = ""
    fixture = {}

    @classmethod
    def setUpClass(cls):
        # from ci import fakedb
        # import json
        # import os
        import importlib
        cls.module_to_test = importlib.import_module(cls.subject_module)
        # from pools import recsys as subject_module
        cls.modname = cls.module_to_test.__name__
        import logging
        log = logging.getLogger(__name__)
        cls.log = log

        from fairways.io import generic as io_generic 
        from fairways import decorators
        from fairways.funcflow import FuncFlow as ff
        cls.ff = ff
        cls.io_generic = io_generic
        cls.decorators = decorators
        import unittest.mock


    
    def get_response_with_fixture(self):
        """
        Test that numbers between 0 and 5 are all even.
        """
        ff = self.ff
        decorators = self.decorators

        entry = ff.find(Channel.items(), lambda r: r.mark_name == "qa" and r.module == self.modname)        
        print(f"Run test: {entry}")

        # entry = self._core.registry.select(self.modname, 'test')
        self.log.debug("ENTRYPOINT: %s", entry)  

        module_conn = decorators.connection.define.find_module_entity(self.modname)
        with unittest.mock.patch.object(module_conn, "subject", self.fixture):
            ctx = {}
            result = entry.handler(ctx)
        
        return result

    def test_with_fixture(self):
        """
        Test that numbers between 0 and 5 are all even.
        """
        # entry = ff.find(Channel.items(), lambda r: r.mark_name == "qa" and r.module == self.modname)        
        # print(f"Run test: {entry}")

        # # entry = self._core.registry.select(self.modname, 'test')
        # self.log.debug("ENTRYPOINT: %s", entry)  

        # module_conn = decorators.connection.define.find_module_entity(self.modname)
        # with unittest.mock.patch.object(module_conn, "subject", self.fixture):
        #     ctx = {}
        #     entry.handler(ctx)
        self.get_response_with_fixture()