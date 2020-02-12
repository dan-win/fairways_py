# -*- coding: utf-8 -*-
"""Flow control for tasks. 
Task flow example:

>>> def fetch_message(message):
...    message = dict(body=message)
...    return message
>>> def transform_message(data):
...     body = data["body"]
...     if body is None:
...         raise ValueError("You should not send empty messages!")
...     body=body[:5]
...     return body
>>> def send_message(message):
...     print(message)
...     return message
>>> def handle_error(err_info):
...     failure = err_info
...     print("Message error:", str(failure))
...     return ""
>>> chain = Chain("Example"
...     ).then(fetch_message
...     ).then(transform_message
...     ).then(send_message
...     ).then(functools.partial(print, "Message sent:")
...     ).catch(handle_error
...     ).then(print)
>>> # "Lazy" chain could be called later:
>>> chain("Hello, World!")
Hello
Message sent: Hello
"""

import os
import sys
import functools
import uuid
import traceback
from abc import abstractmethod
# ? ^ remove

# from inspect import signature
# ? ^ remove

from fairways.funcflow import FuncFlow as ff
from fairways.helpers import (get_nested_default, get_parent, get_lastkey)
from fairways.decorators import typecast

from fairways import log
# import logging
log = log.getLogger()


class Envelope(typecast.FromTypeMixin):
    """Container to pass data between tasks

    :param initial_data: Data to pass. Usually this is Mapping, but you could use another type 
    :type initial_data: Any
    """
    # 2 parts - data and service (CTX, DATA is child of ctx)
    # Each processor has level / visibility mask
    # e.g.: /data/
    # Each Handler has topic which point the root node in data tree (CTX, DATA, or sub-level of DATA)

    ROOT = None
    DATA_ROOT = "data" 
    # DATA_STACK = "stack" 
    FAILURE_ROOT = "failure"

    def __init__(self, *, initial_data, failure_data=None):
        """Constructor method
        """        
        self.state = {
            self.DATA_ROOT: initial_data,
            # self.DATA_STACK: None,
            self.FAILURE_ROOT: failure_data # On failure this memder becomes dict where key is exception classname and value is exception details
        }
    
    @typecast.fromtype('Envelope')
    def _from_obj(self, value):
        self.state = ff.weld(value.state)

    def clone(self):
        """Deep copy of wrapped data and state 
        
        :return: [description]
        :rtype: [type]
        """
        initial_data = ff.deep_extend({}, self.state[self.DATA_ROOT])
        failure_data = ff.deep_extend({}, self.state[self.FAILURE_ROOT])
        return Envelope(initial_data=initial_data, failure_data=failure_data)
    
    def get_ctx(self, attr_path):
        """Get attribute value.
        Nested mappings are supported also.
        You can address values of nested objects using default separator "/"
        Note that internally data is stored as a tree with two branches: DATA_ROOT and FAILURE_ROOT,
        which relates to data of last succesful operation and data related to last failed operation.
        For example, value of key "a" for last successful state looks like "data/a",
        while the same for last failed operation look like "failure/a"


        :param attr_path: Attribute name. Can be complex path separated with "/"
        :type attr_path: str
        :return: Value, related to the attribute name.
        :rtype: Any
        """
        if attr_path:
            return get_nested_default(self.state, attr_path)
        return self.state
    
    def set_ctx(self, attr_path, value):
        """Set attribute value. 
        Nested mappings are supported also.
        You can address values of nested objects using default separator "/".
        Note that internally data is stored as a tree with two branches: DATA_ROOT and FAILURE_ROOT,
        which relates to data of last succesful operation and data related to last failed operation.
        For example, value of key "a" for last successful state looks like "data/a",
        while the same for last failed operation look like "failure/a"
        
        :param attr_path: Attribute name. Can be complex path separated with "/"
        :type attr_path: str
        :param value: New value
        :type value: Any
        """
        # Overwrite entire context, try to keep it immutable (???)
        # data = self.state[self.DATA_ROOT]
        # new_ctx_data = ff.copy(data)
        # if self.isfailure:
        #     new_ctx
        if attr_path:
            # Some child selected
            node = get_parent(self.state, attr_path)
            last_key = get_lastkey(attr_path)
            log.debug("Envelope set_ctx: %s; %s", attr_path, self.state)
            node.update({last_key: value})
        else:
            # Overwrite all
            self.state = value

    def _get_full_data_path(self, *, root=None, topic=None):
        if root is None:
            root = Envelope.DATA_ROOT
        if topic:
            return "/".join([root, topic])
        return root

    # Shortcut, helper:
    def get_data(self, topic=None):
        """Get entire data object for last successful task
        
        :return: Wrapped object
        :rtype: Any
        """
        # # return self.get_ctx(self.DATA_ROOT)
        # if topic:
        #     topic = "/".join([self.DATA_ROOT, topic])
        # else:
        #     topic = self.DATA_ROOT
        # return self.get_ctx(topic)
        attr_path = self._get_full_data_path(topic=topic)
        return get_nested_default(self.state, attr_path)

    def set_data(self, topic=None, value=None):
        """Get entire data object for last successful task
        
        :return: Wrapped object
        :rtype: Any
        """
        attr_path = self._get_full_data_path(topic=topic)
        # self.set_ctx(topic, value)
        node = get_parent(self.state, attr_path)
        last_key = get_lastkey(attr_path)
        log.debug("Envelope set_data: %s; %s; %s; %s", attr_path, node, last_key, self.state)
        node.update({last_key: value})

    def get_failure(self):
        """Get entire data object for last failed task
        
        :return: Wrapped object
        :rtype: Any
        """
        return self.get_ctx(self.FAILURE_ROOT)

    def set_failure(self, failure):
        """Set failure state
        
        :param failure: Failure class instance
        :type failure: Failure
        :raises ValueError: Protects from setting failure to None
        """
        if failure is None:
            raise ValueError("set_failure cannot accept None")
        # if self.state[self.DATA_STACK] is None:
        #     self.state[self.DATA_STACK], self.state[self.DATA_ROOT] = self.state[self.DATA_ROOT], None
        self.state[self.FAILURE_ROOT] = failure

    def reset_failure(self):
        # self.state[self.DATA_ROOT], self.state[self.DATA_STACK] = self.state[self.DATA_STACK], None
        self.state[self.FAILURE_ROOT] = None

    @property    
    def isfailure(self):
        """Flag which is True when current state is a failure
        
        :return: Value
        :rtype: bool
        """
        return bool(self.state[self.FAILURE_ROOT])
    
    @property
    def active_root(self):
        return self.FAILURE_ROOT if self.isfailure else self.DATA_ROOT
    
    def get(self, root, topic):
        attr_path = self._get_full_data_path(root=root, topic=topic)
        return get_nested_default(self.state, attr_path)


class SkipFollowing(Exception):
    """Special class of Exception - Just skip next steps of chain up to nearest catch method

    :param exit_code: User-defined code to distinguish between different cases 
    :type exit_code: Any

    """
    def __init__(self, exit_code, *args, **kwargs):
        """Constructor method
        """
        self.exit_code = exit_code
        super().__init__(*args, **kwargs)


class Failure:
    """Generic exception wrapper for task flow.
    It is a wrapper for standard exceptions with additional metadata.

    :param exception: Exception instance which happens during runtime 
    :type exception: Exception
    :param data_before_failure: Data wrapped in envelope before exception occurs 
    :type data_before_failure: Any
    :param topic: Topic (children path) exception occurs in reducer attached to some topic 
    :type topic: str

    """
    def __init__(self, exception, data_before_failure, method_name=None, topic=None, **kwargs):
        """Constructor method
        """
        self.data_before_failure = data_before_failure
        self.topic = topic
        self.method_name = method_name
        self.details = kwargs

        exc_type, exc_obj, exc_tb = sys.exc_info()
        self.exc_type = exc_type
        self.exc_name = exc_type.__name__
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        self.fname = fname 
        self.line = exc_tb.tb_lineno
        self.ext_info = "\n".join(traceback.format_exception(exc_type, exc_obj,
                                        exc_tb))
    
    def __repr__(self):
        return "Chain failure: {ftype} at method \"{method_name}\" in module {mod_filename} (line {lineno}):\n{ext_info}\n".format(
            ftype=self.exc_name,
            method_name=self.method_name,
            mod_filename=self.fname,
            lineno=self.line,
            # exc_type=self.exc_type,
            # data=self.data_before_failure,
            # details=self.details,
            ext_info=self.ext_info
        )
    
    def __str__(self):
        return "Failure <{}>".format(self.exc_name)
        

        # return f"Chain failure: {self.exc_name} at method \"{self.method}\" in module {self.fname} (line {self.line}) | {self.exception!r}; {self.data_before_failure}; {self.details}"

class Chain:
    """
    Entity which holds sequence of tasks and logic of their mutual flow.
    Allows "lazy" computations after build.

    :param name: Optional name of chain (could be used for debugging) 
    :type topic: str
    """
    # AbsChain, SequentialChain, AndChain, OrChain
    def __init__(self, name=None):
        """Constructor method
        """
        self.name = name or uuid.uuid4()
        self.handlers = []
        self._compiled = None
    
    # def __str__(self):
    #     children = [f.__name__ for (f, topic) in self.fom]
    
    @property
    def compiled(self):
        """Returns list of wrapped methods for chain, with middleware (if any)
        
        :return: List of callables
        :rtype: list
        """
        if self._compiled is None:
            self._compiled = []
            for h in self.handlers:
                rec = (h.render_code(), h.q_topic, h.topic, h.topic_root)
                log.debug("Compiling: %s; %s", rec[1], rec[0])
                self._compiled.append(rec)
        return self._compiled

    def __call__(self,  initial_data, middleware=None):
        """Chain entrypoint
        
        :param initial_data: Initial data to pass into chain (into first task)
        :type initial_data: Any
        :param middleware: Middleware function, which should receive task to wrap, data to pass into task; defaults to None
        :type middleware: Callable(Callable, Any, **Mapping) -> Any, optional
        :return: Data returned by last task
        :rtype: Any
        """
        # Idea add also iter protocol support (?): .next, ...
        envelope = Envelope(initial_data=initial_data)
        for (method, method_q_topic, method_topic, topic_root) in self.compiled:
            is_failure = envelope.isfailure
            active_root = envelope.active_root
            if topic_root != active_root:
                continue # Moving along another branch data/failure
            try:
                data_or_failure = envelope.get(active_root, method_topic)
                
                if data_or_failure is None:
                    continue # Topic not found

                # Extract failure only for top-level handler:
                if is_failure and method_topic is None:
                    failure_rec = envelope.get_failure().copy()
                    exc_name, failure = failure_rec.popitem()
                    data_or_failure = failure
                
                if middleware:
                    data = middleware(method, data_or_failure)
                else:
                    data = method(data_or_failure)

                if is_failure:
                    # Extract failure info and clear failure data at the same time:
                    _, failure = envelope.get_failure().popitem()
                    if data is not None:
                        assert envelope.isfailure == False
                        topic = failure.topic # get last topic before failure
                        # envelope.state[Envelope.DATA_ROOT] = data
                        envelope.set_data(topic, data)
                    # envelope.reset_failure()
                else:
                    envelope.set_data(method_topic, data)

            except Exception as e:
                if is_failure:
                    # Do not allow to raise "nested" exceptions:
                    raise RuntimeError("Critical error - exception inside error handler: %r" % e)
                # data_before_failure = ff.copy(envelope.state[Envelope.DATA_ROOT])
                data_before_failure = ff.copy(envelope.get_data(method_topic))
                failure = Failure(e, data_before_failure, method_name=callable_name(method), topic=method_topic)
                envelope.set_failure({e.__class__.__name__: failure})

        if envelope.isfailure:
            raise RuntimeError(
                "Critical error - cannot access data because exception: %r" % 
                envelope.state[envelope.FAILURE_ROOT])

        return envelope.get_data()
        
    def add_handler(self, handler):
        self.handlers.append(handler)

    # Expose main methods (shortcuts):
    def then(self, method):
        """Append new task (global reducer, which has access to entire structure of data passed to the chain)
        
        :param method: Task function
        :type method: Callable(Any, \**kwargs) -> Any | functools.partial
        :return: Self reference for chaining
        :rtype: taskflow.Chain

        >>> chain = Chain().then(lambda data: data).then(print)
        >>> chain({'a':1})
        {'a': 1}
        """

        h = HandlerThen(method)
        self.add_handler(h)
        return self

    def on(self, keypath, method):
        """Append new task, attached to selected key or path of data. Only this part of data mapping will be passed to a task function. The task function will be called only when related key (or key path when mappings are nested) exists. 
        This approach can be considered as event-based, which allows to build flexible chains without "if". A key (or keypath) can be considered as event and while task function is event handler.
        When value for key path does not exist or when related value is None, attached task will not be called at all. 
        
        :param keypath: Key name (or key path in a form like "a/b/c")
        :type keypath: str
        :param method: Task function
        :type method: Callable(Any, \**kwargs) -> Any | functools.partial
        :return: Self reference for chaining
        :rtype: taskflow.Chain

        >>> chain = Chain().on("a", lambda value: "changed!").then(print)
        >>> chain({"a": "not changed"})
        {'a': 'changed!'}
        >>> chain({"b": "not changed"})
        {'b': 'not changed'}

        """
        # Add narrow/specific reducer with selector
        
        # Arguments:
        #     keypath {string} -- slash-delimited path to target attribute
        #     method {callable} -- reducer code
        
        # Returns:
        #     Chain -- self reference
        
        h = HandlerThen(method, topic=keypath)
        self.add_handler(h)
        return self

    def catch(self, method):
        """Add global interceptor to catch Exception
        
        :param method: Interceptor function
        :type method: Callable(Any, \**kwargs) -> Any | functools.partial
        :return: Self reference for chaining
        :rtype: taskflow.Chain

        >>> chain = Chain().then(lambda _: 1/0).catch(lambda _: "error catched!")
        >>> chain("")
        'error catched!'
        >>> chain = Chain().then(lambda _: 1/0).then(lambda _: "error not catched, step lost!")
        >>> chain("")

        """
        # Add global interceptor to catch Exception
        
        # Arguments:
        #     method {callable} -- interceptor code
        
        # Returns:
        #     Chain -- self reference

        h = HandlerFail(method)
        self.add_handler(h)
        return self

    def catch_on(self, ex_class_or_name, method):
        """Add narrow/specific interceptor with selector.
        Attached handler will be called only on specific exceptions
        
        :param ex_class_or_name: Name or class of a target exception
        :type ex_class_or_name: Class | str
        :param method: Interceptor function
        :type method: Callable(Any, \**kwargs) -> Any | functools.partial
        :raises ValueError: Prevents of "catch_on" usage for Exception instance (use "catch" for this)
        :raises TypeError: Raised when "ex_class_or_name" has invalid type
        :return: Self reference for chaining
        :rtype: taskflow.Chain

        >>> chain = Chain().then(lambda _: 1/0).catch_on(ZeroDivisionError, lambda _: "error catched!")
        >>> chain("")
        'error catched!'
        >>> chain = Chain().then(lambda _: 1/0).catch_on(ValueError, lambda _: "error not catched!")
        >>> chain("")
        
        """

        argtype = type(ex_class_or_name).__name__
        print("REGISTERING ERROR HANDLER::::", argtype)
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

    def trace(self, tracefunc):
        def handler(data):
            tracefunc(data)
            return data
        return self.then(handler)

class Handler:
    topic_root = Envelope.ROOT

    def __init__(self, method, topic = None):
        self.method = method
        self.name = callable_name(method)
        self.topic = topic
        path = []
        if self.topic_root != Envelope.ROOT:
            path.append(self.topic_root)
        if topic:
            path.append(topic)
        self.q_topic = "/".join(path)

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


def callable_name(c):
    "Extract name of function / functools.partial"
    if isinstance(c, functools.partial):
        return c.func.__name__
    else:
        return c.__name__

if __name__ == "__main__":
    import doctest
    print("Doctest: failed: {} / total: {}".format(*doctest.testmod()))