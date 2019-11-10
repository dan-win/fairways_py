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
        from fairways.decorators import (entrypoint, use, entities)
        cls.entrypoint = entrypoint
        cls.entities = entities
        cls.use = use
        cls.os = os

    @classmethod
    def tearDownClass(cls):
        pass

    def test_decorator_tag(self):
        entrypoint = self.entrypoint
        entities = self.entities
        # registry = self.core.registry

        # registry.reset()

        @entrypoint.qa()
        def test_run():
            """DocString"""
            pass
        
        modname = __name__

        # should_be = self.triggers.enum_triggers()
        found = None
        for r in entities.Mark.items():
            if r.mark_name == "qa" and r.module == modname:
                found = r
                break

        self.assertIsNotNone(found)

        should_be = {
            "method": found.handler.__name__,
            "mark_name": found.mark_name,
            "module": found.module,
            "doc": found.doc
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

    def test_cmd_param_run(self):
        entrypoint = self.entrypoint

        @entrypoint.cmd(param="test_command_1")
        def runner(*args, **kwargs):
            return "Command 1 called"
        
        @entrypoint.cmd(param="test_command_2")
        def runner(*args, **kwargs):
            return "Command 2 called"

        result = entrypoint.Cmd.run(args=["--command", "test_command_1"])
        self.assertEqual('Command 1 called', result)

        result = entrypoint.Cmd.run(args=["--command", "test_command_2"])
        self.assertEqual('Command 2 called', result)


if __name__ == '__main__':
    unittest.main(verbosity=2)
