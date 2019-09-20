import unittest


import json
import os

# import sys
# sys.path.insert(0, "../api")
# # from api.underscore import Underscore as _
# from api import underscore


def setUpModule():
    pass

def tearDownModule():
    pass

class UnderscoreTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from api import underscore
        cls.Underscore = underscore.Underscore

    @classmethod
    def tearDownClass(cls):
        pass

    def test_deep_extend(self):
        """
        """
        _ = self.Underscore
        nested_list = [1]
        nested_dict = {"attr1": 1}
        original = {
            "_": "value1",
            "nested_dict": nested_dict,
            "nested_list": nested_list,
        }

        clone = _.deep_extend({}, original)

        self.assertEqual(original, clone, "Clones should have identical values")

        # Change original children:
        nested_list[0] = None
        nested_dict["attr1"] = None

        self.assertNotEqual(clone["nested_list"][0], None,
            "Nested list should be independent instance")
        self.assertNotEqual(clone["nested_dict"]["attr1"], None,
            "Nested dict should be independent instance")
        

class ChainsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from api import chains
        cls.Chain = chains.Chain
        import os
        cls.os = os

    @classmethod
    def tearDownClass(cls):
        pass

    def test_then(self):
        """
        """
        Chain = self.Chain

        arg = "a"

        result = Chain(arg).then(
            lambda a: a + "b"
        ).then(
            lambda a: a + "c"
        ).then(
            lambda a: a + "d"
        ).value

        self.assertEqual(result, "abcd")

    def test_all(self):
        """
        """
        Chain = self.Chain

        arg = 2

        result = Chain(arg).all(
            lambda a: a * 2,
            lambda a: a * 2,
            lambda a: a * 2,
        ).value

        self.assertEqual(result, [4, 4, 4])

    def test_merge(self):
        """
        """
        Chain = self.Chain

        arg = {
            'a': None,
            'b': None,
            'c': None,
        }

        result = Chain(arg).merge(
            lambda a: {'a': 'a'},
            lambda a: {'b': 'b', 'c': '<will be overwritten>'},
            lambda a: {'c': 'c'},
        # ).then(
        #     lambda a: json.dumps(a)
        ).value

        self.assertEqual(result, {"a": "a", "b": "b", "c": "c"})

    def test_middleware(self):
        """
        """
        Chain = self.Chain

        arg = {"data":"X"}

        def mid_pre(method, arg, **kwargs):
            """
            Transforms dict to list of pairs
            """
            arg = list(*arg.items())
            return method(arg)

        def mid_post(method, arg, **kwargs):
            """
            Appends item to the end of list
            """
            result = method(arg)
            result += ["post"]
            return result

        result = Chain(arg).middleware(
            mid_pre,
            mid_post,
        ).then(
            lambda a: a
        ).value

        self.assertEqual(result, ['data', 'X', 'post'])


    def test_middleware_each(self):
        """
        """
        Chain = self.Chain

        arg = {}

        trace = []

        def mid_show_name(method, arg, **kwargs):
            """
            Transforms dict to list of pairs
            """
            trace.append(method.__name__)
            return method(arg)

        def step1(arg):
            return arg

        def step2(arg):
            return arg

        def step3(arg):
            return arg

        result = Chain(arg).middleware(
            mid_show_name,
        ).then(
            step1
        ).then(
            step2
        ).then(
            step3
        ).value

        self.assertEqual(trace, ['step1', 'step2', 'step3'])



    def test_on_if_found(self):
        Chain = self.Chain

        arg = {"data":"should be unchanged", "event": None}

        result = Chain(arg).on(
            "event",
            lambda _: "modified!"
        ).value

        self.assertEqual(result, {'data': 'should be unchanged', 'event': 'modified!'})
        
    def test_on_if_not_found(self):
        Chain = self.Chain

        arg = {"data":"should be unchanged", "alien-event": 1}

        result = Chain(arg).on(
            "event",
            lambda e: e+1
        ).value

        self.assertEqual(result, {'data': 'should be unchanged', 'alien-event': 1})



    def test_nested_on_if_found(self):
        Chain = self.Chain

        arg = {"data":"should be unchanged", "event": None}
        tree = {"nested": arg}

        result = Chain(tree).on(
            "nested/event",
            lambda _: "modified!"
        ).value

        self.assertEqual(result, {'nested': {'data': 'should be unchanged', 'event': 'modified!'}})
        
    def test_nested_on_if_not_found(self):
        Chain = self.Chain

        arg = {"data":"should be unchanged", "alien-event": 1}
        tree = {"nested": arg}

        result = Chain(tree).on(
            "nested/event",
            lambda e: e+1
        ).value

        self.assertEqual(result, {'nested': {'alien-event': 1, 'data': 'should be unchanged'}})

    def test_with_env(self):
        """
        """
        Chain = self.Chain

        @Chain.with_env(**{"test": 1, "newkey": 2})
        def func(data, env=None):
            return env

        result = func(None)
        self.assertEqual(result, {'newkey': 2, 'test': 1})

    def test_with_env_var(self):
        """
        """
        Chain = self.Chain
        os = self.os

        os.environ['TEST_VAR'] = 'TEST_VALUE'
        
        @Chain.with_env_vars('TEST_VAR')
        def func(data, env=None):
            return env

        result = func(None)
        self.assertEqual(result, {'TEST_VAR':'TEST_VALUE'})

    def test_with_env_addition(self):
        """
        """
        Chain = self.Chain

        @Chain.with_env(**{"env1": 1})
        @Chain.with_env(**{"env2": 1})
        @Chain.with_env(**{"env3": 1})
        def func(data, env=None):
            return env

        result = func(None)
        self.assertEqual(result, {'env1': 1, 'env2': 1, 'env3': 1})


class DecoratorsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from api import core, triggers
        from api.decorators import entrypoint
        cls.entrypoint = entrypoint
        cls.core = core
        cls.triggers = triggers

    @classmethod
    def tearDownClass(cls):
        pass

    def test_decorator_cron(self):
        """
        """
        entrypoint = self.entrypoint
        # registry = self.core.registry

        # registry.reset()

        @entrypoint.cron(seconds=100)
        def test_run():
            pass
        
        modname = __name__

        # should_be = self.triggers.enum_triggers()
        r = self.triggers.enum_triggers(module_name=modname, tag="cron")

        # r = registry.cron

        should_be = {
            "method": r[0]["method"].__name__,
            "seconds": r[0]["seconds"],
            "module": r[0]["module_name"],
        }

        self.assertEqual(len(r), 1)

        self.assertEqual(should_be, {'method': 'test_run', 'seconds': 100, 'module': __name__})


class DbiTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from api.io import (DbTaskSetManager, DbTaskSet, Query, FixtureQuery, DbDriver)
        cls.DbTaskSetManager = DbTaskSetManager
        cls.DbTaskSet = DbTaskSet
        cls.Query = Query
        cls.FixtureQuery = FixtureQuery
        cls.DbDriver = DbDriver

    @classmethod
    def tearDownClass(cls):
        pass

    def test_create(self):
        """
        """
        DbTaskSetManager = self.DbTaskSetManager
        DbTaskSet = self.DbTaskSet
        Query = self.Query
        DbDriver = self.DbDriver

        manager = DbTaskSetManager()

        @manager.set_dba
        class TestDb(DbTaskSet):
            QUERY1 = Query(
                "select * from t1",
                "DB_CONN",
                lambda x: x
            )

        @DbTaskSetManager.inject_dba_decorator(manager)
        def test(ctx, dba=None, unused_arg=None):
            return dba

        db = test(None)

        attrs = [name for name in dir(db) if not name.startswith('_')]
        # self.assertEqual(attrs, ['queries'])
        self.assertTrue(isinstance(db.QUERY1, Query))

    def test_create_fixture(self):
        """
        """
        DbTaskSetManager = self.DbTaskSetManager
        DbTaskSet = self.DbTaskSet
        Query = self.Query
        DbDriver = self.DbDriver
        FixtureQuery = self.FixtureQuery

        manager = DbTaskSetManager()

        @manager.set_dba
        class TestDb(DbTaskSet):
            QUERY1 = Query(
                "select * from t1",
                "DB_CONN",
                lambda x: x
            )

        @DbTaskSetManager.inject_dba_decorator(manager)
        def test(ctx, dba=None, unused_arg=None):
            return dba

        self.assertEqual(test(None).__name__, 'TestDb', 
            "Current DbTaskSetManager should be same as used for last 'use_db' invocation")

        manager.add_fixture("MyLocalFixture",
            QUERY1 = [{"name": "value"}]
        )

        saved = manager.select_profile("MyLocalFixture")

        fixture = test(None)

        print("Test stringify behaviour: %s" % fixture)

        self.assertEqual(fixture.QUERY1.get_records(), [{'name': 'value'}])
        self.assertEqual(test(None).__name__, 'MyLocalFixture')

        manager.select_profile(saved)

        self.assertEqual(test(None).__name__, 'TestDb', 
            "Current DbTaskSet should be same as used for last 'set_module_db_taskset' invocation")

    def test_create_fixture_context(self):
        """
        """
        DbTaskSetManager = self.DbTaskSetManager
        DbTaskSet = self.DbTaskSet
        Query = self.Query
        DbDriver = self.DbDriver
        FixtureQuery = self.FixtureQuery

        manager = DbTaskSetManager()

        @manager.set_dba
        class TestDb(DbTaskSet):
            QUERY1 = Query(
                "select * from t1",
                "DB_CONN",
                lambda x: x
            )

        @DbTaskSetManager.inject_dba_decorator(manager)
        def test(ctx, dba=None, unused_arg=None):
            return dba

        self.assertEqual(test(None).__name__, 'TestDb', 
            "Current DbTaskSetManager should be same as used for last 'use_db' invocation")

        manager.add_fixture("MyLocalFixture",
            QUERY1 = [{"name": "value"}]
        )
        
        with manager.another_context("MyLocalFixture"):

            fixture = test(None)

            print("Test stringify behaviour: %s" % fixture)

            self.assertEqual(fixture.QUERY1.get_records(), [{'name': 'value'}])
            self.assertEqual(test(None).__name__, 'MyLocalFixture')

        self.assertEqual(test(None).__name__, 'TestDb', 
            "Profile should be restored after exit form contexdt manager")


if __name__ == '__main__':
    unittest.main(verbosity=2)
