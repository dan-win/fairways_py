# -*- coding: utf-8 -*-

from .underscore import Underscore as _

# TO-DO: move to rust with multiprocessing!
class Chain:
    """
    Chainable sequence to route data amoung "processors" (any callable)
    """
    def __init__(self, some_data):
        if callable(some_data):
            some_data = some_data(None)
        self.data = some_data
        self.middleware_items = []
    
    def middleware(self, *items):
        def check_callable(item):
            if callable(item):
                return item
            raise TypeError("Middleware should be callable: {!r}".format(item))
        self.middleware_items = _.map(items, check_callable)
        return self
    
    def call_wrapped(self, method, arg):
        arg = _.deep_extend(arg)
        if self.middleware_items:
            for middleware_item in self.middleware_items:
                arg = middleware_item(method, arg)
        else:
            arg = method(arg)
        return arg

    def then(self, method):
        """
        """
        arg = self.data
        result = self.call_wrapped(method, arg)
        return Chain(result)
    
    def all(self, *methods_list):
        """
        Executes all methods, puts results into array
        """
        results = []
        arg = self.data
        for method in methods_list:
            result = self.call_wrapped(method, arg)
            results.append(result)
        return Chain(results)

    def merge(self, *methods_list):
        """
        Executes all methods, merges results into dict
        """
        results = {}
        arg = self.data
        for method in methods_list:
            result = self.call_wrapped(method, arg)
            results.update(result)
        return Chain(results)

    @property
    def value(self):
        return _.deep_extend(self.data)


