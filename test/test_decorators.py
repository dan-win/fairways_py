import unittest


import json
import os


def setUpModule():
    pass

def tearDownModule():
    pass


class DecoratorsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # from fairways.api import core, triggers
        from fairways.decorators import (entrypoint, use)
        cls.entrypoint = entrypoint
        cls.use = use
        cls.os = os

    @classmethod
    def tearDownClass(cls):
        pass

    def test_decorator_tag(self):
        entrypoint = self.entrypoint
        # registry = self.core.registry

        # registry.reset()

        @entrypoint.qa()
        def test_run():
            """DocString"""
            pass
        
        modname = __name__

        # should_be = self.triggers.enum_triggers()
        found = None
        for r in entrypoint.Channel.items():
            if r.mark_name == "qa" and r.module == modname:
                found = r
                break

        # r = self.triggers.enum_triggers(module_name=modname, tag="cron")

        # r = registry.cron

        should_be = {
            "method": r.handler.__name__,
            "mark_name": r.mark_name,
            "module": r.module,
            "doc": r.doc
        }

        self.assertIsNotNone(found)

        self.assertEqual(should_be, {
            'method': 'test_run', 
            'mark_name': 'qa', 
            'module': __name__,
            'doc': 'DocString'})

    def test_with_env(self):
        """
        """
        use = self.use

        @use.env(**{"test": 1, "newkey": 2})
        def func(data, env=None):
            return env

        result = func(None)
        self.assertEqual(result, {'newkey': 2, 'test': 1})

    def test_with_env_var(self):
        """
        """
        use = self.use
        os = self.os

        os.environ['TEST_VAR'] = 'TEST_VALUE'
        
        @use.env_vars('TEST_VAR')
        def func(data, env=None):
            return env

        result = func(None)
        self.assertEqual(result, {'TEST_VAR':'TEST_VALUE'})

    def test_with_env_addition(self):
        """
        """
        use = self.use

        @use.env(**{"env1": 1})
        @use.env(**{"env2": 1})
        @use.env(**{"env3": 1})
        def func(data, env=None):
            return env

        result = func(None)
        self.assertEqual(result, {'env1': 1, 'env2': 1, 'env3': 1})


if __name__ == '__main__':
    unittest.main(verbosity=2)
