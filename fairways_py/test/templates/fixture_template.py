import unittest

from ci.utils import csv2py

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
        from api import (core, triggers)
        cls.triggers = triggers
        cls._core = core
        log = logging.getLogger(__name__)
        cls.log = log

    def test_with_fixture(self):
        """
        Test that numbers between 0 and 5 are all even.
        """
        # for i in range(0, 6):
        #     with self.subTest(i=i):
        #         self.assertEqual(i % 2, i % 2)
        # self.log.debug("REGISTRY: %s", self._core.registry)
        # entry = self._core.registry.test[self.modname]['method']
        print("", __name__, self.triggers.enum_triggers())
        
        entry = self.triggers.enum_module_triggers(self.modname, tag="test")[0]["method"]
        
        print("entry:::::", entry)

        # entry = self._core.registry.select(self.modname, 'test')
        self.log.debug("ENTRYPOINT: %s", entry)        
        entry({"fixture": self.fixture})