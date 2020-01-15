# -*- coding: utf-8 -*-
"""Tools are for basic operations with mappings and iterables.
Chaining support to avoid intermediate variables.
Inspired by Underscore.js: https://underscorejs.org.
Despite that, a lot of methods have different naming and behaviour.
"""

import copy
import collections

class FuncFlow(object):
    """ This class contains functions to operate with mappings and iterables.
    """

    @staticmethod
    def deep_extend(*args):
        """Deep copy of each item into leftmost argument
        When attribute itself is a mapping or iterable, it would be copied recursively

        :args: 
            *args: Mapping items to combine their attributes from leftmost to rightmost step-by-step. Note that the leftmost item will be updated during this operation!
        :raises TypeError: Unsupported type
        :return: Mapping where attributes are combined, rightmost args have higher precedence
        :rtype: Mapping
        >>> FuncFlow.deep_extend({}, {'name': 'moe'}, {'age': 50}, {'name': 'new'}, {'nested':{'some': 1}})
        {'name': 'new', 'age': 50, {'nested':{'some': 1}}}
        """
        def clone_obj(item):
            if isinstance(item, collections.abc.Mapping):
                return {k:v for (k, v) in item.items()}
            if isinstance(item, (list, tuple)):
                return list(item)
            return None

        def iterator(item, i, iterable):
            obj = clone_obj(item)
            if obj is None:
                iterable[i] = item
            else:
                if isinstance(obj, collections.Mapping):
                    iterable[i] = FuncFlow.deep_extend({}, obj)
                elif isinstance(obj, (list, tuple)):
                    FuncFlow.each(obj, iterator)
                    iterable[i] = obj
                else:
                    raise TypeError("deep_copy cannot handle this type: {}".format(type(obj)))
            
        args = list(args)
        dest = args.pop(0)

        for source in args:
            if source:
                for k, v in source.items():
                    obj = clone_obj(v)
                    if obj is None:
                        dest[k] = v
                    else:
                        FuncFlow.each(obj, iterator)
                        dest[k] = obj
        return dest

    @staticmethod
    def uniq(iterable):
        """Make set of distinct values from Iterable
        
        :param iterable: Source iterable
        :type iterable: Iterable
        :return: List of unique values. Note that values can be out of order
        :rtype: list
        >>> FuncFlow.uniq([1, 2, 1, 4, 1, 3])
        [1, 2, 4, 3]
        """
        if iterable is None: return None
        return list(set(list(iterable)))

    @staticmethod
    def filter(iterable, iterfunc):
        """Filter iterable members with a rule defined as a function
        
        :param iterable: Source iterable
        :type iterable: Iterable
        :param iterfunc: Rule to filter items, should return Truish value to select item into result
        :type iterfunc: Callable
        :return: Filtered subset
        :rtype: list
        >>> FuncFlow.filter([1, 2, 3, 4, 5, 6], lambda v: v % 2 == 0)
        [2,4,6]
        """
        if iterable is None: return None
        return [item for item in iterable if iterfunc(item)]
    
    @staticmethod
    def reduce(iterable, iterfunc, memo):
        """Compute single result from iterable using supplied function
        
        :param iterable: Source iterable
        :type iterable: Iterable
        :param iterfunc: Function which receives item from source iterable and current value of memo and returns memo updated
        :type iterfunc: Callable (Any, Any) -> Any
        :param memo: Initial value of combined result
        :type memo: Any
        :return: Reduced item (its type depends on type of memo)
        :rtype: Any
        >>> FuncFlow.reduce([1, 2, 3], lambda memo, num: memo + num, 0)
        6
        """
        for item in iterable:
            memo = iterfunc(memo, item)
        return memo

    @staticmethod
    def extend(*args):
        """Swallow copy of each item.
        When attribute itself is a mapping or iterable, it would be copied "by reference"
        
        :args: 
            *args: Mapping items to combine their attributes from leftmost to rightmost step-by-step. Note that the leftmost item will be updated during this operation!
        :return: Mapping where attributes are combined, rightmost args have higher precedence
        :rtype: Mapping
        >>> FuncFlow.extend({}, {'name': 'moe'}, {'age': 50}, {'name': 'new'})
        {'name': 'new', 'age': 50}
        """
        # Note: In the current implementation it uses deep extend under the hood
        return FuncFlow.deep_extend(*args)
        # args = list(args)
        # dest = args.pop(0)
        # for source in args:
        #     if source:
        #         dest.update(source)
        # return dest

    @staticmethod
    def weld(*args):
        """Similar to deep_extend, but returns entirely new dict, wwithout modifications in a leftmost item.
        
        :args: 
            *args: Mapping items to combine their attributes from leftmost to rightmost step-by-step. All items will be unchanged.
        :return: Mapping where attributes are combined, rightmost args have higher precedence
        :rtype: Dict
        >>> FuncFlow.weld({'name': 'moe'}, {'age': 50}, {'name': 'new'})
        {'name': 'new', 'age': 50}
        """
        return FuncFlow.deep_extend({}, *args)

    @staticmethod
    def omit(data, *keys):
        """Build dict from the source mapping, without specified keys
        
        :param data: Source mapping
        :type data: Mapping
        :param *keys: List of keys which should not present in result
        :return: Mapping where 
        :rtype: Dict
        >>> FuncFlow.omit({'name': 'moe', 'age': 50, 'userid': 'moe1'}, 'userid')
        {'name': 'moe', 'age': 50}
        """
        if data is None: return None
        return {k: v for k, v in data.items() if k not in keys}

    @staticmethod
    def pick(data, *keys):
        """Build dict from the source mapping, with specified keys only.
        This is opposite operation for omit.
        
        :param data: Source mapping
        :type data: Mapping
        :param *keys: List of keys which should present in result
        :return: Mapping where 
        :rtype: Dict
        >>> FuncFlow.pick({'name': 'moe', 'age': 50, 'userid': 'moe1'}, 'name', 'age')
        {'name': 'moe', 'age': 50}
        """
        if data is None: return None
        existing = set(data.keys())
        return {k: data[k] for k in keys if k in existing}

    @staticmethod
    def contains(iterable, value):
        """Test whether iterable contains specified value
        
        :param iterable: Source iterable
        :type iterable: Iterable
        :param value: Value to search
        :type value: Any
        :return: Result of test
        :rtype: bool
        >>> FuncFlow.contains([1, 2, 3], 3)
        True
        >>> FuncFlow.contains([1, 2, 3], 1000)
        False
        """
        return value in iterable
    
    @staticmethod
    def count_by(iterable, iterfunc):
        """Count items with grouping in accordance with rules
        
        :param iterable: Source iterable
        :type iterable: Iterable
        :param iterfunc: Function which map item to some group
        :type iterfunc: Callable
        :return: Mapping where keas are groups and values are items count per group
        :rtype: Dict
        >>> FuncFlow.count_by([1, 2, 3, 4, 5], lambda num: 'even' if num % 2 == 0 else 'odd')
        {'odd': 3, 'even': 2}
        """
        result = {}
        for item in iterable:
            key = iterfunc(item)
            result[key] = result.get(key, 0) + 1
        return result

    @staticmethod
    def each(iterable, iterfunc):
        """Apply iterable to each item.
        Note that this function returns no result!
        
        :param iterable: Source iterable
        :type iterable: Iterable[Any]
        :param iterfunc: Iterator function which receives 3 arguments -value, index or key, and the source iterable itself
        :type iterfunc: Callable(Any, Any, Iterable) -> None
        """
        iterator = iterable
        if isinstance(iterable, dict):
            for key, value in iterable.items():
                iterfunc(value, key, iterable)
        else:
            for i, value in enumerate(iterable):
                iterfunc(value, i, iterable)

    @staticmethod
    def every(iterable, iterfunc):
        """Returns true if all of the values in the list pass the predicate truth test
        
        :param iterable: Source
        :type iterable: Iterable
        :param iterfunc: Function which tests item and returns boolean value
        :type iterfunc: Callable(Any) -> bool
        :return: Test result
        :rtype: bool
        >>> FuncFlow.every([2, 4, 5], lambda num: num % 2 == 0)
        False
        >>> FuncFlow.every([3, 6, 9], lambda num: num % 3 == 0)
        True
        """
        if iterable is None: return None
        return FuncFlow.reduce(iterable, lambda memo, v: memo and bool(iterfunc(v)), True)

    @staticmethod
    def find(iterable, iterfunc):
        """Looks through each value in the list, returning the first one that passes a truth test (predicate), or None if no value passes the test.
        
        :param iterable: Source iterable
        :type iterable: Iterable
        :param iterfunc: Function which tests item and returns boolean value
        :type iterfunc: Callable(Any) -> bool
        :return: First item which meets criteria
        :rtype: Any
        >>> FuncFlow.find([1, 2, 3, 4, 5, 6], lambda num: num % 2 == 0)
        2
        """
        if iterable is None: return None
        for item in iterable:
            if iterfunc(item):
                return item
        return None

    @staticmethod
    def find_where(iterable, **properties):
        """Looks through the list and returns the first value that matches all of the key-value pairs listed in properties
        
        :param iterable: Source iterable
        :type iterable: Iterable
        :return: First item which meets criteria
        :rtype: Any
        >>> test_data = [
        ...    {"name":"John", "age":25, "occupation":"soldier"},
        ...    {"name":"Jim", "age":30, "occupation":"actor"},
        ...    {"name":"Jane", "age":25, "occupation":"soldier"},
        ...    {"name":"Joker", "age":50, "occupation":"actor"},
        ...    {"name":"Jarvis", "age":100, "occupation":"mad scientist"},
        ...    {"name":"Jora", "age":5, "occupation":"child"}]
        >>> criteria = {"age": 25, "occupation":"soldier"}
        >>> FuncFlow.find_where(test_data, **criteria)
        {'name': 'John', 'age': 25, 'occupation': 'soldier'}
        """
        if iterable is None: return None
        result = []
        for item in iterable:
            flag = True
            for key, value in properties.items():
                if not item[key] == value:
                    flag = False
                    break
            if flag:
                # result.append(item)
                return item
        return None

    @staticmethod
    def map(iterable, iterfunc):
        """Build new iterable where each item modified by function providen
        
        :param iterable: Source iterable
        :type iterable: Iterable
        :param iterfunc: Function which computes new item value using previous one
        :type iterfunc: Callable(Any) -> Any
        :return: Entirely new list with modified items
        :rtype: list
        >>> FuncFlow.map([1, 2, 3, 4, 5, 6], lambda num: num * 2)
        {"a":2, "b":4, "c":6, "d":8, "e":10, "f":12}
        """
        if iterable is None: return None
        if isinstance(iterable, dict):
            return {k:iterfunc(v, k) for k, v in iterable.items()}
        return [iterfunc(item) for item in iterable]

    @staticmethod
    def group_by(iterable, iteratee):
        """Splits a collection into sets, grouped by the result of running each value through iteratee. If iteratee is a string instead of a function, groups by the property named by iteratee on each of the values
        
        :param iterable: Source iterable
        :type iterable: Iterable
        :param iteratee: Function which returns group for item (or a string name of key to group by it)
        :type iteratee: Callable(Any) -> Any
        :raises TypeError: Throws exception if second argument neither callable nor string
        :return: Mapping where keys are groups and values are lists of related items
        :rtype: Dict
        >>> FuncFlow.group_by(["London", "Paris", "Lissabon", "Perth"], lambda s: s[:1])
        {'L': ['London', 'Lissabon'], 'P': ['Paris', 'Perth']}
        """
        if iterable is None: return None
        if isinstance(iteratee, str):
            attrname = iteratee
            method = lambda v: v[attrname]
        elif callable(iteratee):
            method = iteratee
        else:
            raise TypeError()
        
        def grouper(memo, v):
            key = method(v)
            return FuncFlow.extend(memo, {
                key: memo.get(key, []) + [v]
            })

        return FuncFlow.reduce(iterable, grouper, {})

    @staticmethod
    def index_by(iterable, iteratee):
        """Given an iterable, and an iteratee function that returns a key for each element (or a property name), returns a dict with a key of each item. 
        Just like group_by, but for when you know your keys are unique.
        
        :param iterable: Source iterable
        :type iterable: Iterable
        :param iteratee: Function which returns key for item (or a string name of key to index by it)
        :type iteratee: Callable(Any) -> Any
        :raises TypeError: Throws exception if second argument neither callable nor string
        :return: Mapping where keys are groups and values are lists of related items
        :rtype: Dict
        """
        if iterable is None: return None
        if isinstance(iteratee, str):
            attrname = iteratee
            method = lambda v: v[attrname]
        elif callable(iteratee):
            method = iteratee
        else:
            raise TypeError()
        
        def grouper(memo, v):
            key = method(v)
            return FuncFlow.extend(memo, {
                key: v
            })

        return FuncFlow.reduce(iterable, grouper, {})

    @staticmethod
    def pluck(iterable, propname):
        """Enumerate unique values of key for all items in iterable
        
        :param iterable: Source iterable
        :type iterable: Iterable[Mapping]
        :param propname: Name of key
        :type propname: str
        :return: List of unique values
        :rtype: list
        """
        return FuncFlow.uniq(FuncFlow.map(iterable, lambda v: v[propname]))
    
    @staticmethod
    def sort_by(iterable, iterfunc):
        """Sort items using function and return new list without modifications in a source one
        
        :param iterable: Source iterable
        :type iterable: Iterable[Any]
        :param iterfunc: Function which maps item to any value which is suitable for ordering (int, str, ...)
        :type iterfunc: Callable(Any) -> Any
        :return: New list
        :rtype: list
        """
        return sorted(iterable, key=iterfunc)

    @staticmethod
    def chain(object):
        """Wraps value in a chainable object which allows to apply FuncFlow methods sequentially.
        To unwrap the result, use .value property
        
        :param object: Source object
        :type object: Any
        :return: Chainable object
        :rtype: Chain
        """
        return Chain(object)
    
    @staticmethod
    def size(iterable):
        """Return length of iterable
        
        :param iterable: Source iterable
        :type iterable: Iterable
        :return: Length
        :rtype: int
        """
        return len(list(iterable))
    
    @staticmethod
    def copy(iterable):
        """Make deep copy of iterable.
        Wrapper for chaining.
        Uses Python copy.deepcopy.
        Note that the source should support pickle operation

        :param iterable: Source iterble
        :type iterable: Iterable
        :return: New copy
        :rtype: Iterable
        """
        return copy.deepcopy(iterable)

    @staticmethod
    def apply(object, func):
        """Apply function to entire object at once.
        Wrapper for chaining

        :param object: Source object 
        :type object: Mapping | Iterable
        :param func: Function to apply
        :type func: Callable(Any) -> Any
        :return: Result of the specified function
        :rtype: Any
        """
        return func(object)

class Chain(object):
    """ Chainable object which allow to return new instance of Chain after most operations of FuncFlow.

    :param object: Source object 
    :type object: Mapping | Iterable
    """
    def __init__(self, data):
        """Constructor method
        """        
        if data is None:
            raise TypeError('Cannot operate with NoneType!')
        self._data = data
    
    def _method(self, name):
        method = getattr(FuncFlow, name)
        def wrapper(*args, **kwargs):
            data = _align_type(self._data)
            self._data = method(data, *args, **kwargs)
            return self
        return wrapper

    
    def __getattribute__(self, name):
        if name in dir(FuncFlow):
            return self._method(name)
        return object.__getattribute__(self, name)
    
    def saveto(self, writer, slice=None):
        """Helper which allows to output intermediate result using writer function.
        
        :param writer: Function which outputs the current value of chain somwhere (console, file, etc)
        :type writer: Callable[Any]
        :param slice: Count of elements to limit output length, defaults to None
        :type slice: int, optional
        :return: chain object itself, without modification
        :rtype: Chain
        """
        data = _align_type(self._data)
        if slice:
            if isinstance(data, dict):
                data = { k:v for (k, v) in data.items()[:slice] }
            else:
                data = list(data)[:slice]
        writer(data)
        return self
    
    @property
    def value(self):
        """Unwrap value of chain object
        
        :return: Current value of chain object
        :rtype: Any
        """
        return _align_type(self._data)


def _align_type(data):
    if data is None:
        return data
    if isinstance(data, (int, bool, float, str, object, dict)):
        return data
    # if isinstance(data, dict):
    #     return dict(data)
    else:
        return list(data)


