# -*- coding: utf-8 -*-

import os
import functools

from inspect import signature

from .funcflow import FuncFlow as ff
from .helpers import (get_nested, get_parent, get_lastkey)

class Failure:
    def __init__(self, exception):
        self.exception = exception
    
    def __str__(self):
        return f"Chain failure: {self.exception}"

# TO-DO: move to rust with multiprocessing!
class Chain:
    """
    Chainable sequence to route data amoung "processors" (any callable)
    """
    def __init__(self, initial_ctx, middleware_items=None):
        """[summary]
        
        Arguments:
            initial_ctx {any|Chain|callable} -- Initial context for chain input
        
        Keyword Arguments:
            middleware_items {[type]} -- [description] (default: {None})
            step {int} -- [description] (default: {1})
            failure {Failure} -- [failure on previous spet] (default: None)
        """
        self.failure = None
        step = 0
        inherited_middleware = []

        if isinstance(initial_ctx, Chain):
            chain = initial_ctx
            initial_ctx = chain.ctx
            del chain.ctx
            if chain.failure is not None:
                self.failure = chain.failure
                del chain.failure
            if chain.middleware_items:
                inherited_middleware = chain.middleware_items[:]
                del chain.middleware_items
            step = chain.step + 1
        elif callable(initial_ctx):
            initial_ctx = initial_ctx(None)

        self.ctx = initial_ctx
        middleware = middleware_items or inherited_middleware
        self.middleware(*middleware)
        self.step = step

    # def __del__(self):
    #     try:
    #         self.ctx = None
    #         self.middleware = None
    #     except:
    #         pass

    # def next_chain(self, ctx):
    #     middleware = self.middleware[:]
    #     c = Chain(ctx)
    #     c.step = self.step + 1
    #     c.failure = self.failure
    #     return c
    
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
        self.middleware_items = ff.map(items, check_callable)
        return self
    
    def _call_wrapped(self, method, ctx):
        ctx_0 = ff.deep_extend(ctx)
        try:
            if self.middleware_items:
                for middleware_item in self.middleware_items:
                    ctx = middleware_item(method, ctx, **{"__step": self.step})
            else:
                ctx = method(ctx)
        except Exception as e:
            self.failure = Failure(e)
            # Return last "successful" ctx
            # return ff.deep_extend(ctx_0)
            return ctx_0
        return ctx

    def then(self, method):
        """Attach action to next node of chain
        
        Arguments:
            method {callable} -- Custom action, accepts chained data, returns changed copy of data
        
        Returns:
            Chain<any> -- Next node with a wrapped result of action
        """
        if self.failure is None:
            ctx = self.ctx
            self.ctx = self._call_wrapped(method, ctx)
            if self.ctx is None:
                raise TypeError("Chained method \"{}\" should not return None".format(method.__name__))
        return Chain(self)
    
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
        if self.failure is None:
            ctx = self.ctx
            try:
                value = get_nested(ctx, keypath)
                parent = get_parent(ctx, keypath)
            except KeyError:
                # This is not an error - do nothing if key is absent
                return self

            result = self._call_wrapped(method, value)
            last_key = get_lastkey(keypath)
            parent.update({
                last_key: result
            })
            self.ctx = ctx
        return Chain(self)

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
        if self.failure is None:
            results = []
            ctx = self.ctx
            for method in methods_list:
                result = self._call_wrapped(method, ctx)
                if self.failure:
                    return Chain(self)
                results.append(result)
            self.ctx = results
        return Chain(self)

    def merge(self, *methods_list):
        """Executes all methods, merges results into dict. 
        Each action should return a dict 
        
        Returns:
            Chain<dict> -- Next node with dict where results merged via dict.update()
        """
        if self.failure is None:
            results = {}
            ctx = self.ctx
            for method in methods_list:
                result = self._call_wrapped(method, ctx)
                if self.failure:
                    return Chain(self)
                results.update(result)
            self.ctx = results
        return Chain(self)
    
    def catch(self, err_method):
        ctx = self.ctx
        if self.failure is not None:
            last_failure = self.failure
            self.failure = None
            # ctx = self._call_wrapped(method, ctx)
            result = err_method(last_failure)

        return Chain(self)

    @property
    def value(self):
        """Unwrapped value of chain
        
        Returns:
            Any -- Unwrapped value
        """
        return ff.deep_extend(self.ctx)


