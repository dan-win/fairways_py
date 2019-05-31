import unittest


import json


# import sys
# sys.path.insert(0, "../hostapi")
# # from hostapi.underscore import Underscore as _
# from hostapi import underscore

print("================>Ok")

def setUpModule():
    pass

def tearDownModule():
    pass

class UnderscoreTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from hostapi import underscore
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

        original_snapshot = json.dumps(original)

        clone = _.deep_extend({}, original)

        # Change original children:
        nested_list[0] = None
        nested_dict["attr1"] = None

        self.assertNotEqual(clone["nested_list"][0], None,
            "Nested list should be independent instance")
        self.assertNotEqual(clone["nested_dict"]["attr1"], None,
            "Nested dict should be independent instance")
        
        clone_str = json.dumps(clone)
        self.assertEqual(original_snapshot, clone_str)


class ChainsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from hostapi import chains
        cls.Chain = chains.Chain

    @classmethod
    def tearDownClass(cls):
        pass

    def test_then(self):
        """
        """
        import json
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
        import json
        Chain = self.Chain

        arg = 2

        result = Chain(arg).all(
            lambda a: a * 2,
            lambda a: a * 2,
            lambda a: a * 2,
        ).then(
            lambda a: json.dumps(a)
        ).value

        self.assertEqual(result, "[4, 4, 4]")

    def test_merge(self):
        """
        """
        import json
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
        ).then(
            lambda a: json.dumps(a)
        ).value

        self.assertEqual(result, '{"a": "a", "b": "b", "c": "c"}')

    def test_middleware(self):
        """
        """
        import json
        Chain = self.Chain

        arg = {"data":"X"}

        def mid_pre(method, arg):
            """
            Transforms dict to list of pairs
            """
            arg = list(*arg.items())
            return method(arg)

        def mid_post(method, arg):
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


# if __name__ == '__main__':
#     unittest.main(verbosity=2)
