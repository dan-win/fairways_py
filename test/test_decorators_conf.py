import unittest


import json
import os


def setUpModule():
    pass

def tearDownModule():
    pass


class ConfigTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from fairways.decorators import use
        from fairways import conf
        cls.use = use
        cls.conf = conf

        class TestSettings:
            def __init__(self, key1, key2):
                self.KEY1 = key1
                self.KEY2 = key2
                self.LOGGING = {}
                self.CONNECTIONS = {}
        
        cls.settings_factory = TestSettings

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # Cleanup settings, simulate fresh load
        self.conf.settings = None


    def test_decorator_before_conf_load(self):
        """
        """
        use = self.use
        conf = self.conf
        settings_factory = self.settings_factory

        settings = settings_factory("VALUE1", "VALUE2")

        result = {}

        # 1. Register decorator
        @use.config("KEY2")
        def set_conf(sub_conf):
            result.update({"config": sub_conf})
        
        # 2. Load conf
        conf.load(settings)

        self.assertDictEqual(result, {'config': 'VALUE2'})


    def test_decorator_after_conf_load(self):
        """
        """
        use = self.use
        conf = self.conf
        settings_factory = self.settings_factory

        settings = settings_factory("VALUE1", "VALUE2")

        result = {}

        # 1. Load conf
        conf.load(settings)

        # 2. Register decorator
        @use.config("KEY2")
        def set_conf(sub_conf):
            result.update({"config": sub_conf})
        
        self.assertDictEqual(result, {'config': 'VALUE2'})


    def test_decorated_direct_call(self):
        """
        """
        pass


        # self.assertEqual(steps_count, 6, "Some steps were not executed")
        # self.assertTrue(jumps_to_second.search(line) is not None, "No transitions to second thread")
        # self.assertTrue(jumps_to_first.search(line) is not None, "No transitions to first thread")

