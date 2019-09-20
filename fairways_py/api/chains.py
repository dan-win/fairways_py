# -*- coding: utf-8 -*-

import os
import functools

from inspect import signature

from .underscore import Underscore as _
from .helpers import (get_nested, get_parent, get_lastkey)

# TO-DO: move to rust with multiprocessing!
class Chain:
    """
    Chainable sequence to route data amoung "processors" (any callable)
    """
    def __init__(self, initial_ctx, middleware_items=None, step=1):
        """[summary]
        
        Arguments:
            initial_ctx {any|Chain|callable} -- Initial context for chain input
        
        Keyword Arguments:
            middleware_items {[type]} -- [description] (default: {None})
            step {int} -- [description] (default: {1})
        """
        if isinstance(initial_ctx, Chain):
            chain = initial_ctx
            initial_ctx = initial_ctx.value
            step = chain.step
        elif callable(initial_ctx):
            initial_ctx = initial_ctx(None)
        self.ctx = initial_ctx
        middleware = middleware_items or []
        self.middleware(*middleware)
        self.step = step
    
    def middleware(self, *items):
        """Install middleware for subsequent nodes of chain.
        Middleware is a callable with protocol (method, value).
        You could modify data passed to action and/or its result.
        
        Raises:
            TypeError: When middleware passed in is not a callable
        
        Returns:
            Chain instance -- next node to continue chaining, all subsequent action will be wrapped with middleware
        """
        def check_callable(item):
            if callable(item):
                return item
            raise TypeError("Middleware should be callable: {!r}".format(item))
        self.middleware_items = _.map(items, check_callable)
        return self
    
    def _call_wrapped(self, method, ctx):
        ctx = _.deep_extend(ctx)
        if self.middleware_items:
            for middleware_item in self.middleware_items:
                ctx = middleware_item(method, ctx, **{"__step": self.step})
        else:
            ctx = method(ctx)

        return ctx

    def then(self, method):
        """Attach action to next node of chain
        
        Arguments:
            method {callable} -- Custom action, accepts chained data, returns changed copy of data
        
        Returns:
            Chain<any> -- Next node with a wrapped result of action
        """
        ctx = self.ctx
        result = self._call_wrapped(method, ctx)
        if result is None:
            raise TypeError("Chained method \"{}\" should not return None".format(method.__name__))
        return Chain(result, self.middleware_items, self.step+1)
    
    def on(self, keypath, method):
        """Fires action only when selected key exists in chained data 
        (certainly, data in the chain data should be a dict:).
        Other keys passes throught this step unmodified (transparently)
        
        Arguments:
            keypath {str} -- Path of value in a chained data dict (certainly, ctx should be a dict in such case)
            method {callable} -- Action of node
        
        Returns:
            Chain<dict> -- Next node where dicts' nested attribute (defined by "keypath") is updated by action 
        """
        ctx = self.ctx
        try:
            value = get_nested(ctx, keypath)
            parent = get_parent(ctx, keypath)
        except KeyError:
            return self

        result = self._call_wrapped(method, value)
        last_key = get_lastkey(keypath)
        parent.update({
            last_key: result
        })
        return Chain(ctx, self.middleware_items, self.step+1)



        # if keyname in arg.keys():
        #     result = self._call_wrapped(method, arg[keyname])
        #     arg.update({
        #         keyname: result
        #     })
        #     return Chain(arg)
        # else:
        #     return self

    
    def all(self, *methods_list):
        """Executes all methods from a list, 
        puts results into array
        
        Returns:
            Chain<list> -- Next node with list where items are results of actions.
            NOTE: Chained data becomes a list of results per each action
        """
        results = []
        ctx = self.ctx
        for method in methods_list:
            result = self._call_wrapped(method, ctx)
            results.append(result)
        return Chain(results, self.middleware_items, self.step+1)

    def merge(self, *methods_list):
        """Executes all methods, merges results into dict. 
        Each action should return a dict 
        
        Returns:
            Chain<dict> -- Next node with dict where results merged via dict.update()
        """
        results = {}
        ctx = self.ctx
        for method in methods_list:
            result = self._call_wrapped(method, ctx)
            results.update(result)
        return Chain(results, self.middleware_items, self.step+1)

    @property
    def value(self):
        """Unwrapped value of chain
        
        Returns:
            Any -- Unwrapped value
        """
        return _.deep_extend(self.ctx)


