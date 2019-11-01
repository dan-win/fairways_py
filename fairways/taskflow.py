# -*- coding: utf-8 -*-

import os
import sys
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
        """Set failure state
        
        Arguments:
            failure {Failure} -- Failure class instance
        
        Raises:
            ValueError: Protects from setting failure to None
        """
        if failure is None:
            raise ValueError("set_failure cannot accept None")
        self.state[self.DATA_STACK], self.state[self.DATA_ROOT] = self.state[self.DATA_ROOT], None
        self.state[self.FAILURE_ROOT] = failure

    def reset_failure(self):
        self.state[self.DATA_ROOT], self.state[self.DATA_STACK] = self.state[self.DATA_STACK], None
        self.state[self.FAILURE_ROOT] = None

    @property    
    def isfailure(self):
        """Whether is failure state now
        
        Returns:
            bool -- True when failure state
        """
        return self.state[self.FAILURE_ROOT] is not None


class SkipFollowing(Exception):
    "Just skip next steps of chain"
    def __init__(self, exit_code, *args, **kwargs):
        self.exit_code = exit_code
        super().__init__(*args, **kwargs)


class Failure(Exception):
    def __init__(self, exception, data_before_failure, method=None, topic=None, **kwargs):
        self.exception = exception
        self.data_before_failure = data_before_failure
        self.details = kwargs

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        self.exc_type = exc_type.__name__
        self.method = method
        self.topic = topic
        self.fname = fname 
        self.line = exc_tb.tb_lineno
    
    def __str__(self):
        return f"Chain failure: {self.exc_type} at method \"{self.method}\" in module {self.fname} (line {self.line}) | {self.exception!r}; {self.data_before_failure}; {self.details}"

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

    def __call__(self,  initial_data, middleware=None):
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
                    if data is not None:
                        envelope.state[Envelope.DATA_ROOT] = data
                else:
                    envelope.setval(topic, data)

            except Exception as e:
                data_before_failure = ff.copy(envelope.state[Envelope.DATA_ROOT])
                failure = Failure(e, data_before_failure, method=method.__name__, topic=topic)
                envelope.set_failure({e.__class__.__name__: failure})
                log.debug(f"[E] Running '{method.__name__}'; topic: '{topic}'; envelope: {envelope.state}")

        return envelope.get_data()
        
    def add_handler(self, handler):
        self.handlers.append(handler)

    # Expose main methods (shortcuts):
    def then(self, method):
        """Add global reducer 
        
        Arguments:
            method {callable} -- reducer code
        
        Returns:
            Chain -- self reference
        """
        h = HandlerThen(method)
        self.add_handler(h)
        return self

    def on(self, keypath, method):
        """Add narrow/specific reducer with selector
        
        Arguments:
            keypath {string} -- slash-delimited path to target attribute
            method {callable} -- reducer code
        
        Returns:
            Chain -- self reference
        """
        h = HandlerThen(method, topic=keypath)
        self.add_handler(h)
        return self

    def catch(self, method):
        """Add global interceptor to catch Exception
        
        Arguments:
            method {callable} -- interceptor code
        
        Returns:
            Chain -- self reference
        """
        h = HandlerFail(method)
        self.add_handler(h)
        return self

    def catch_on(self, ex_class_or_name, method):
        """Add narrow/specific interceptor with selector
        
        Arguments:
            ex_class_or_name {str|class} -- [description]
            method {callable} -- [description]
        
        Raises:
            ValueError: [description]
            TypeError: [description]
        
        Returns:
            Chain -- self reference
        """
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


