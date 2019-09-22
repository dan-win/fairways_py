import unittest

import fairways

from fairways.ci.utils import csv2py

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

    def test_with_fixture(self):
        """
        Test that numbers between 0 and 5 are all even.
        """
        entry = _.find(Channel.items(), lambda r: r.channel_tag == "qa" and r.module == self.modname)        
        print("entry:::::", entry)

        # entry = self._core.registry.select(self.modname, 'test')
        self.log.debug("ENTRYPOINT: %s", entry)        
        entry({"fixture": self.fixture})