# -*- coding: utf-8 -*-

import os
import functools
import uuid

from abc import abstractmethod
# ? ^ remove

from inspect import signature
# ? ^ remove

from .funcflow import FuncFlow as ff
from .helpers import (get_nested_default, get_parent, get_lastkey)

import logging
log = logging.getLogger()


class Envelope:
    # 2 parts - data and service (CTX, DATA is child of ctx)
    # Each processor has level / visibility mask
    # e.g.: /data/
    # Each Handler has topic which point the root node in data tree (CTX, DATA, or sub-level of DATA)

    ROOT = None
    DATA_ROOT = "data" 
    DATA_STACK = "stack" 
    FAILURE_ROOT = "failure"

    def __init__(self, initial_data):
        self.state = {
            self.DATA_ROOT: initial_data,
            self.DATA_STACK: None,
            self.FAILURE_ROOT: None # On failure this memder becomes dict where key is exception classname and value is exception details
        }

    @abstractmethod
    def clone(self):
        return ff.deep_extend({}, self.state)
    
    def getval(self, attr_path):
        return get_nested_default(self.state, attr_path)
    
    def setval(self, attr_path, value):
        node = get_parent(self.state, attr_path)
        last_key = get_lastkey(attr_path)
        log.debug(f"Envelope setval: {attr_path}; {self.state}")
        node.update({last_key: value})

    # Shortcut, helper:
    def get_data(self):
        return self.getval(self.DATA_ROOT)

    def get_failure(self):
        return self.getval(self.FAILURE_ROOT)

    def set_failure(self, failure):
        if failure is None:
            raise ValueError("set_failure cannot accept None")
        self.state[self.DATA_STACK], self.state[self.DATA_ROOT] = self.state[self.DATA_ROOT], None
        self.state[self.FAILURE_ROOT] = failure

    def reset_failure(self):
        self.state[self.DATA_ROOT], self.state[self.DATA_STACK] = self.state[self.DATA_STACK], None
        self.state[self.FAILURE_ROOT] = None

    @property    
    def isfailure(self):
        return self.state[self.FAILURE_ROOT] is not None


class SkipFollowing(Exception):
    "Just skip next steps of chain"



class Failure(Exception):
    def __init__(self, exception, **kwargs):
        self.exception = exception
        self.details = kwargs
    
    def __str__(self):
        return f"Chain failure: {self.exception}; {self.exception!r}; {self.details}"

class Chain:
    # AbsChain, SequentialChain, AndChain, OrChain
    def __init__(self, name=None):
        self.name = name or uuid.uuid4()
        self.handlers = []
        self._compiled = None
    
    # def __str__(self):
    #     children = [f.__name__ for (f, topic) in self.fom]
    
    @property
    def compiled(self):
        if self._compiled is None:
            self._compiled = []
            for h in self.handlers:
                rec = (h.render_code(), h.topic)
                log.debug(f"Compiling: {rec[1]}; {rec[0]} ")
                self._compiled.append(rec)
        return self._compiled

    def __call__(self, 
        initial_data, 
        middleware=None
        ):
        # Idea add also iter protocol support (?): .next, ...
        envelope = Envelope(initial_data)
        for (method, topic) in self.compiled:
            try:
                data = envelope.getval(topic)
                prefix = '[F]' if envelope.isfailure else '[S]'
                if data is None:
                    continue # Topic not found
                log.debug(f"{prefix} Running '{method.__name__}'; topic: '{topic}'; envelope: {envelope.state}; getval: {data}")
                if middleware:
                    data = middleware(method, data)
                else:
                    data = method(data)
                if envelope.isfailure:
                    envelope.reset_failure()
                else:
                    envelope.setval(topic, data)

            except Exception as e:
                failure = Failure(e)
                envelope.set_failure({e.__class__.__name__: failure})
                log.warning(f"[E] Running '{method.__name__}'; topic: '{topic}'; envelope: {envelope.state}")

        return envelope.get_data()
    
    # def to_middleware(self):
    #     # Use self as middleware for "func"
    #     def wrapper(method, args, **kwargs):
    #         def adapter(own_method, data):
    #             method, args, kwargs = data
    #             return own_method(method, args, **kwargs)
    #         return self.__call__((method, args, kwargs), adapter)
    #     return wrapper
    
    def add_handler(self, handler):
        self.handlers.append(handler)

    # Expose main methods (shortcuts):
    def then(self, method):
        h = HandlerThen(method)
        self.add_handler(h)
        return self

    def on(self, keypath, method):
        h = HandlerThen(method, topic=keypath)
        self.add_handler(h)
        return self

    def catch(self, method):
        h = HandlerFail(method)
        self.add_handler(h)
        return self

    def catch_on(self, ex_class_or_name, method):
        argtype = type(ex_class_or_name).__name__
        if argtype == 'str':
            keypath = ex_class_or_name
        elif argtype in ('type', 'classobj'):
            keypath = ex_class_or_name.__name__
            if keypath == 'Exception':
                raise ValueError('Use .catch() instead of .catch_on() to handle basic Exception')
        else:
            raise TypeError("catch_on argument ex_class_or_name should be string or exception class")
        h = HandlerFail(method, topic=keypath)
        self.add_handler(h)
        return self

class Handler:
    topic_root = Envelope.ROOT

    def __init__(self, method, topic = None):
        self.method = method
        self.name = method.__name__
        path = []
        if self.topic_root != Envelope.ROOT:
            path.append(self.topic_root)
        if topic is not None:
            path.append(topic)
        if len(path) > 0:
            self.topic = "/".join(path)
        else: 
            self.topic = self.topic_root

    # @staticmethod
    # def register_handler(cls):
    #     """Decorator to register plug-ins"""
    #     name = cls.handler_name
    #     registry[name] = cls

    #     setattr(sys.modules[source_module], name, cls)
    #     return cls

    def render_code(self):
        return self.method

class HandlerThen(Handler):
    topic_root = Envelope.DATA_ROOT

class HandlerFail(Handler):
    topic_root = Envelope.FAILURE_ROOT

class ChainAny(Chain):
    pass 

class ChainAll(Chain):
    pass 


# # TO-DO: move to rust with multiprocessing!
# class Chain:
#     """
#     Chainable sequence to route data amoung "processors" (any callable)
#     """
#     def __init__(self, initial_ctx, middleware_items=None):
#         """[summary]
        
#         Arguments:
#             initial_ctx {any|Chain|callable} -- Initial context for chain input
        
#         Keyword Arguments:
#             middleware_items {[type]} -- [description] (default: {None})
#             step {int} -- [description] (default: {1})
#             failure {Failure} -- [failure on previous spet] (default: None)
#         """
#         self.failure = None
#         step = 0
#         inherited_middleware = []

#         if isinstance(initial_ctx, Chain):
#             chain = initial_ctx
#             initial_ctx = chain.ctx
#             del chain.ctx
#             if chain.failure is not None:
#                 self.failure = chain.failure
#                 del chain.failure
#             if chain.middleware_items:
#                 inherited_middleware = chain.middleware_items[:]
#                 del chain.middleware_items
#             step = chain.step + 1
#         elif callable(initial_ctx):
#             initial_ctx = initial_ctx(None)

#         self.ctx = initial_ctx
#         middleware = middleware_items or inherited_middleware
#         self.middleware(*middleware)
#         self.step = step
    
#     def middleware(self, *items):
#         """Install middleware for subsequent nodes of chain.
#         Middleware is a callable with protocol (method, value).
#         You could modify data passed to action and/or its result.
        
#         Raises:
#             TypeError: When middleware passed in is not a callable
        
#         Returns:
#             Chain instance -- next node to continue chaining, all subsequent action will be wrapped with middleware
#         """
#         def check_callable(item):
#             if callable(item):
#                 return item
#             raise TypeError("Middleware should be callable: {!r}".format(item))
#         self.middleware_items = ff.map(items, check_callable)
#         return self
    
#     def _call_wrapped(self, method, ctx):
#         ctx_0 = ff.deep_extend(ctx)
#         try:
#             if self.middleware_items:
#                 for middleware_item in self.middleware_items:
#                     ctx = middleware_item(method, ctx, **{"__step": self.step})
#             else:
#                 ctx = method(ctx)
#         except Exception as e:
#             self.failure = Failure(e, at=f'method: {method.__name__}; module: {method.__module__}')
#             # Return last "successful" ctx
#             # return ff.deep_extend(ctx_0)
#             return ctx_0
#         return ctx

#     def then(self, method):
#         """Attach action to next node of chain
        
#         Arguments:
#             method {callable} -- Custom action, accepts chained data, returns changed copy of data
        
#         Returns:
#             Chain<any> -- Next node with a wrapped result of action
#         """
#         if self.failure is None:
#             ctx = self.ctx
#             self.ctx = self._call_wrapped(method, ctx)
#             if self.ctx is None:
#                 raise TypeError("Chained method \"{}\" should not return None".format(method.__name__))
#         return Chain(self)
    
#     def on(self, keypath, method):
#         """Fires action only when selected key exists in chained data 
#         (certainly, data in the chain data should be a dict:).
#         Other keys passes throught this step unmodified (transparently)
        
#         Arguments:
#             keypath {str} -- Path of value in a chained data dict (certainly, ctx should be a dict in such case)
#             method {callable} -- Action of node
        
#         Returns:
#             Chain<dict> -- Next node where dicts' nested attribute (defined by "keypath") is updated by action 
#         """
#         if self.failure is None:
#             ctx = self.ctx
#             try:
#                 value = get_nested(ctx, keypath)
#                 parent = get_parent(ctx, keypath)
#             except KeyError:
#                 # This is not an error - do nothing if key is absent
#                 return self

#             result = self._call_wrapped(method, value)
#             last_key = get_lastkey(keypath)
#             parent.update({
#                 last_key: result
#             })
#             self.ctx = ctx
#         return Chain(self)

#         # if keyname in arg.keys():
#         #     result = self._call_wrapped(method, arg[keyname])
#         #     arg.update({
#         #         keyname: result
#         #     })
#         #     return Chain(arg)
#         # else:
#         #     return self

    
#     def all(self, *methods_list):
#         """Executes all methods from a list, 
#         puts results into array
        
#         Returns:
#             Chain<list> -- Next node with list where items are results of actions.
#             NOTE: Chained data becomes a list of results per each action
#         """
#         if self.failure is None:
#             results = []
#             ctx = self.ctx
#             for method in methods_list:
#                 result = self._call_wrapped(method, ctx)
#                 if self.failure:
#                     return Chain(self)
#                 results.append(result)
#             self.ctx = results
#         return Chain(self)

#     def merge(self, *methods_list):
#         """Executes all methods, merges results into dict. 
#         Each action should return a dict 
        
#         Returns:
#             Chain<dict> -- Next node with dict where results merged via dict.update()
#         """
#         if self.failure is None:
#             results = {}
#             ctx = self.ctx
#             for method in methods_list:
#                 result = self._call_wrapped(method, ctx)
#                 if self.failure:
#                     return Chain(self)
#                 results.update(result)
#             self.ctx = results
#         return Chain(self)
    
#     def catch(self, err_method):
#         ctx = self.ctx
#         if self.failure is not None:
#             last_failure = self.failure
#             self.failure = None
#             # ctx = self._call_wrapped(method, ctx)
#             result = err_method(last_failure)

#         return Chain(self)

#     @property
#     def value(self):
#         """Unwrapped value of chain
        
#         Returns:
#             Any -- Unwrapped value
#         """
#         return ff.deep_extend(self.ctx)


# class SkipFollowing(Exception):
#     "Just skip next steps of chain"

