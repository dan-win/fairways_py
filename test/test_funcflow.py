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
        
        self.assertEqual(ff.deep_extend({'a': {'b': 2}}, {'a': {'b': 3, 'd': 4}, 'e': 5}), {'a': {'b': 3, 'd': 4}, 'e': 5})
        
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

        class Summ:
            def __init__(self):
                self.value = 0
            def __call__(self, value, key, iterable):
                self.value += value
                # ff.count_by([1, 2, 3, 4, 5]

        sum = Summ()        
        ff.each([1, 2, 3, 4, 5], sum)
        self.assertEqual(15, sum.value)

        sum = Summ()        
        ff.each({"a":1, "b":2, "c":3, "d":4, "e":5}, sum)
        self.assertEqual(15, sum.value)

    def test_every(self):
        """
        Returns true if all of the values in the list pass the predicate truth test
        """
        ff = self.FuncFlow

        result = ff.every([2, 4, 5], lambda num: num % 2 == 0)
        self.assertEqual(result, False)

        result = ff.every([3, 6, 9], lambda num: num % 3 == 0)
        self.assertEqual(result, True)


    def test_find(self):
        """
        Looks through each value in the list, returning the first one that passes a truth test (predicate), or None if no value passes the test.
        """
        ff = self.FuncFlow

        result = ff.find([1, 2, 3, 4, 5, 6], lambda num: num % 2 == 0)
        self.assertEqual(result, 2)

    def test_find_where(self):
        """
        Looks through the list and returns the first value that matches all of the key-value pairs listed in properties.
        """
        ff = self.FuncFlow
        test_data = [
            {"name":"John", "age":25, "occupation":"soldier"},
            {"name":"Jim", "age":30, "occupation":"actor"},
            {"name":"Jane", "age":25, "occupation":"soldier"},
            {"name":"Joker", "age":50, "occupation":"actor"},
            {"name":"Jarvis", "age":100, "occupation":"mad scientist"},
            {"name":"Jora", "age":5, "occupation":"child"},
        ]
        criteria = {"age": 25, "occupation":"soldier"}
        result = ff.find_where(test_data, **criteria)

        self.assertEqual(result, {'name': 'John', 'age': 25, 'occupation': 'soldier'})

    def test_map(self):
        """
        """
        ff = self.FuncFlow

        result = ff.map([1, 2, 3, 4, 5, 6], lambda num: num * 2)
        self.assertEqual(result, [2, 4, 6, 8, 10, 12], "Should operate with lists")

        result = ff.map({"a":1, "b":2, "c":3, "d":4, "e":5, "f":6}, lambda num, key: num * 2)
        self.assertEqual(result, {"a":2, "b":4, "c":6, "d":8, "e":10, "f":12}, "Should operate with lists")

    def test_group_by(self):
        """
        Splits a collection into sets, grouped by the result of running each value through iteratee. If iteratee is a string instead of a function, groups by the property named by iteratee on each of the values.
        """
        ff = self.FuncFlow

        result = ff.group_by(["London", "Paris", "Lissabon", "Pert"], lambda s: s[:1])
        self.assertEqual(result, {'L': ['London', 'Lissabon'], 'P': ['Paris', 'Pert']})

        test_data = [
            {"name":"John", "age":25, "occupation":"soldier"},
            {"name":"Jim", "age":30, "occupation":"actor"},
            {"name":"Jane", "age":25, "occupation":"soldier"},
            {"name":"Joker", "age":50, "occupation":"actor"},
            {"name":"Jarvis", "age":100, "occupation":"mad scientist"},
            {"name":"Jora", "age":5, "occupation":"child"},
        ]
        result = ff.group_by(test_data, "occupation")
        self.assertEqual(result, {
            'actor': [
                    {'age': 30, 'name': 'Jim', 'occupation': 'actor'},
                    {'age': 50, 'name': 'Joker', 'occupation': 'actor'}],
            'child': [{'age': 5, 'name': 'Jora', 'occupation': 'child'}],
            'mad scientist': [{'age': 100,
                     'name': 'Jarvis',
                     'occupation': 'mad scientist'}],
            'soldier': [
                    {'age': 25, 'name': 'John', 'occupation': 'soldier'},
                    {'age': 25, 'name': 'Jane', 'occupation': 'soldier'}]}
            )


    def test_index_by(self):
        """
        Given a list, and an iteratee function that returns a key for each element in the list (or a property name), returns an object with an index of each item. Just like groupBy, but for when you know your keys are unique.
        """
        ff = self.FuncFlow
        
        test_data = [
            {"name":"John", "age":25, "occupation":"soldier"},
            {"name":"Jim", "age":30, "occupation":"actor"},
            {"name":"Jane", "age":25, "occupation":"soldier"},
            {"name":"Joker", "age":50, "occupation":"actor"},
            {"name":"Jarvis", "age":100, "occupation":"mad scientist"},
            {"name":"Jora", "age":5, "occupation":"child"},
        ]
        result = ff.index_by(test_data, "name")
        self.assertEqual(result, {
            "John": {"name":"John", "age":25, "occupation":"soldier"},
            "Jim":{"name":"Jim", "age":30, "occupation":"actor"},
            "Jane":{"name":"Jane", "age":25, "occupation":"soldier"},
            "Joker":{"name":"Joker", "age":50, "occupation":"actor"},
            "Jarvis":{"name":"Jarvis", "age":100, "occupation":"mad scientist"},
            "Jora":{"name":"Jora", "age":5, "occupation":"child"},

        })

    def test_pluck(self):
        """
        """
        ff = self.FuncFlow

        test_data = [{'name': 'moe', 'age': 40}, {'name': 'larry', 'age': 50}, {'name': 'curly', 'age': 60}]

        result = ff.pluck(test_data, "name")

        self.assertEqual(result, ['moe', 'larry', 'curly'])

    def test_sort_by(self):
        """
        """
        ff = self.FuncFlow

        result = ff.sort_by([5, 4, 6, 3, 1000, 200], lambda value: str(value))

        self.assertEqual(result, [1000, 200, 3, 4, 5, 6])

    def test_size(self):
        """
        """
        ff = self.FuncFlow

        result = ff.size([5, 4, 6, 3, 1000, 200])

        self.assertEqual(result, 6)

    def test_apply(self):
        """
        Apply function once to entire object and return result
        """
        ff = self.FuncFlow

        result = ff.apply([5, 4, 6, 3, 1000, 200], lambda v: len(v))

        self.assertEqual(result, 6)

    def test_chain(self):
        """
        Allow to weld sequential calls to single expression
        """
        ff = self.FuncFlow

        result = ff.chain([1,2]).sort_by(lambda v: -v).map(str).apply(",".join).value

        self.assertEqual(result, '2,1')

if __name__ == '__main__':
    unittest.main(verbosity=2)
