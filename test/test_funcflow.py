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
        
    def test_uniq(self):
        """
        """
        ff = self.FuncFlow

        result = ff.uniq([1, 2, 1, 4, 1, 3])
        self.assertEqual(result, [1, 2, 4, 3])

    def test_filter(self):
        """
        """
        ff = self.FuncFlow

        evens = ff.filter([1, 2, 3, 4, 5, 6], lambda v: v % 2 == 0)

        self.assertEqual(evens, [2,4,6])

    def test_reduce(self):
        """
        """
        ff = self.FuncFlow

        sum = ff.reduce([1, 2, 3], lambda memo, num: memo + num, 0)

        self.assertEqual(sum, 6)

    def test_extend(self):
        """
        """
        ff = self.FuncFlow

        result = ff.extend({}, {'name': 'moe'}, {'age': 50}, {'name': 'new'})

        self.assertEqual(result, {'name': 'new', 'age': 50})

    def test_omit(self):
        """
        """
        ff = self.FuncFlow

        result = ff.omit({'name': 'moe', 'age': 50, 'userid': 'moe1'}, 'userid')

        self.assertEqual(result, {'name': 'moe', 'age': 50})

    def test_pick(self):
        """
        """
        ff = self.FuncFlow
        result = ff.pick({'name': 'moe', 'age': 50, 'userid': 'moe1'}, 'name', 'age')

        self.assertEqual(result, {'name': 'moe', 'age': 50})

    def test_contains(self):
        """
        """
        ff = self.FuncFlow

        self.assertEqual(ff.contains([1, 2, 3], 3), True)
        self.assertEqual(ff.contains([1, 2, 3], 1000), False)

    def test_count_by(self):
        """
        """
        ff = self.FuncFlow

        result = ff.count_by([1, 2, 3, 4, 5], lambda num: \
            'even' if num % 2 == 0 else 'odd')

        self.assertEqual(result, {'odd': 3, 'even': 2})

    def test_each(self):
        """
        """
        ff = self.FuncFlow

        result = {'values': '', 'keys': ''}
        # def iteratee(value, key, iterable):
        #     result


        self.assertEqual(result, [])

    def test_every(self):
        """
        """
        ff = self.FuncFlow

        self.assertEqual(result, [])

    def test_find(self):
        """
        """
        ff = self.FuncFlow

        self.assertEqual(result, [])

    def test_find_where(self):
        """
        """
        ff = self.FuncFlow

        self.assertEqual(result, [])

    def test_map(self):
        """
        """
        ff = self.FuncFlow

        self.assertEqual(result, [])

    def test_group_by(self):
        """
        """
        ff = self.FuncFlow

        self.assertEqual(result, [])

    def test_index_by(self):
        """
        """
        ff = self.FuncFlow

        self.assertEqual(result, [])

    def test_pluck(self):
        """
        """
        ff = self.FuncFlow

        self.assertEqual(result, [])

    def test_sort_by(self):
        """
        """
        ff = self.FuncFlow

        self.assertEqual(result, [])

    def test_size(self):
        """
        """
        ff = self.FuncFlow

        self.assertEqual(result, [])

    def test_apply(self):
        """
        """
        ff = self.FuncFlow

        self.assertEqual(result, [])

    def test_chain(self):
        """
        """
        ff = self.FuncFlow

        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main(verbosity=2)
