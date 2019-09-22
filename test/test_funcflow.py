import unittest


import json
import os

def setUpModule():
    pass

def tearDownModule():
    pass

class FuncFlowTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from fairways import funcflow
        cls.FuncFlow = funcflow.FuncFlow

    @classmethod
    def tearDownClass(cls):
        pass

    def test_deep_extend(self):
        """
        """
        ff = self.FuncFlow
        nested_list = [1]
        nested_dict = {"attr1": 1}
        original = {
            "_": "value1",
            "nested_dict": nested_dict,
            "nested_list": nested_list,
        }

        clone = ff.deep_extend({}, original)

        self.assertEqual(original, clone, "Clones should have identical values")

        # Change original children:
        nested_list[0] = None
        nested_dict["attr1"] = None

        self.assertNotEqual(clone["nested_list"][0], None,
            "Nested list should be independent instance")
        self.assertNotEqual(clone["nested_dict"]["attr1"], None,
            "Nested dict should be independent instance")
        



if __name__ == '__main__':
    unittest.main(verbosity=2)
