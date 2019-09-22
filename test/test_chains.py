import unittest


import json
import os


def setUpModule():
    pass

def tearDownModule():
    pass


class ChainsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from fairways import chains
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





if __name__ == '__main__':
    unittest.main(verbosity=2)
