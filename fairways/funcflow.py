# -*- coding: utf-8 -*-
"""
These functions are ported (with some modifications) from Underscore.js: https://underscorejs.org
"""

import copy
import collections

class FuncFlow(object):

    @staticmethod
    def deep_extend(*args):
        """
        Deep copy of each item ("extend" makes swallow copy!)
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
        if iterable is None: return None
        return list(set(list(iterable)))

    @staticmethod
    def filter(iterable, iterfunc):
        if iterable is None: return None
        return [item for item in iterable if iterfunc(item)]
    
    @staticmethod
    def reduce(iterable, iterfunc, memo):
        for item in iterable:
            memo = iterfunc(memo, item)
        return memo

    @staticmethod
    def extend(*args):
        # Note: Always use deep_extend. It returns correct result when structures becomes nested:)
        return FuncFlow.deep_extend(*args)
        # args = list(args)
        # dest = args.pop(0)
        # for source in args:
        #     if source:
        #         dest.update(source)
        # return dest

    @staticmethod
    def weld(*args):
        return FuncFlow.deep_extend({}, *args)

    @staticmethod
    def omit(data, *keys):
        if data is None: return None
        return {k: v for k, v in data.items() if k not in keys}

    @staticmethod
    def pick(data, *keys):
        if data is None: return None
        existing = set(data.keys())
        return {k: data[k] for k in keys if k in existing}

    @staticmethod
    def contains(iterable, value):
        return value in iterable
    
    @staticmethod
    def count_by(iterable, iterfunc):
        result = {}
        for item in iterable:
            key = iterfunc(item)
            result[key] = result.get(key, 0) + 1
        return result

    @staticmethod
    def each(iterable, iterfunc):
        iterator = iterable
        if isinstance(iterable, dict):
            for key, value in iterable.items():
                iterfunc(value, key, iterable)
        else:
            for i, value in enumerate(iterable):
                iterfunc(value, i, iterable)

    @staticmethod
    def every(iterable, iterfunc):
        if iterable is None: return None
        return FuncFlow.reduce(iterable, lambda memo, v: memo and bool(iterfunc(v)), True)

    @staticmethod
    def find(iterable, iterfunc):
        if iterable is None: return None
        for item in iterable:
            if iterfunc(item):
                return item
        return None

    @staticmethod
    def find_where(iterable, **properties):
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
        if iterable is None: return None
        if isinstance(iterable, dict):
            return {k:iterfunc(v, k) for k, v in iterable.items()}
        return [iterfunc(item) for item in iterable]

    @staticmethod
    def group_by(iterable, iteratee):
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
        return FuncFlow.uniq(FuncFlow.map(iterable, lambda v: v[propname]))
    
    @staticmethod
    def sort_by(iterable, iterfunc):
        return sorted(iterable, key=iterfunc)

    @staticmethod
    def chain(object):
        return Chain(object)
    
    @staticmethod
    def size(iterable):
        return len(list(iterable))
    
    @staticmethod
    def copy(iterable):
        return copy.deepcopy(iterable)

    @staticmethod
    def apply(object, func):
        """Aply passed function to passed object at once
        
        Arguments:
            object {any} -- data to process
            func {callable} -- function to apply
        
        Returns:
            any -- result of func
        """
        return func(object)

class Chain(object):
    def __init__(self, data):
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


