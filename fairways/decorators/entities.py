"Special marks for module executables which plays some special role"

from ..funcflow import FuncFlow as ff

import logging
log = logging.getLogger(__name__)

import functools

from enum import Enum

DECORATORS = dict()

import sys
def register_decorator(cls):
    """Decorator to register plug-ins"""
    name = cls.mark_name
    DECORATORS[name] = cls
    source_module = cls.__module__
    # setattr(sys.modules[__name__], name, cls)
    setattr(sys.modules[source_module], name, cls)
    return cls

class RegistryItem:
    def __init__(self, **attrs):
        self.subject = attrs["subject"]
        self.meta = attrs["meta"]
        self.mark_name = attrs["mark_name"]
        self.module = attrs["module"]
        self.doc = attrs["doc"]
    
    def __str__(self):
        return f"Registry Item: '{self.module}:{self.mark_name}' / object: '{self.subject.__name__}'"

class Mark:
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    mark_name = "mark"

    registry_item_class = RegistryItem

    decorator_kwargs = []
    decorator_required_kwargs = []

    once_per_module = True

    _registry = []

    # def fmt_route(self):

    def __init__(self, **options):
        options = ff.pick(options, *(self.decorator_kwargs))
        missed = [k for k in self.decorator_required_kwargs if k not in options.keys()]
        if len(missed) > 0:
            raise TypeError("Decorator {} - required args missed: {}".format(self.__class__.__name__, ",".join(missed)))
        self.options = options
        # log.debug('Decorator: %s', self)
    
    def __str__(self):
        return self.mark_name

    def __call__(self, subject):
        if self.once_per_module and self.__class__.__name__ != Mark.__name__:
            if self.find_module_entity(subject.__module__):
                raise Exception(f"Mark '{self.mark_name}' alredy defined in module '{subject.__module__}'")
        self._registry += [self.registry_item_class(
            subject=subject,
            meta=ff.extend({}, self.options),
            mark_name=self.mark_name,
            module=subject.__module__,
            doc=subject.__doc__,
        )]
        log.debug('Decorator called: %s', self.mark_name)
        return subject

    @classmethod
    def items(cls):
        if cls.__name__ == Mark.__name__:
            return iter(cls._registry)
        return ff.filter(cls._registry, lambda v: v.mark_name == cls.mark_name)

    @classmethod
    def find_module_entity(cls, module_name):
        if cls.__name__ == Mark.__name__:
            raise TypeError("find_module_entity applicable to Mark descendants only")
        return ff.find(
            cls.items(), 
            lambda r: r.module == module_name)

    @classmethod
    def chain(cls):
        return ff.chain(cls.items())
    
    @classmethod
    def reset_registry(cls):
        own_items = cls.items()
        new_registry = []
        for item in cls._registry:
            if item in own_items:
                continue
            new_registry.append(item)
        cls._registry = new_registry

