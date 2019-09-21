from api.underscore import Underscore as _

import logging
log = logging.getLogger(__name__)

from enum import Enum

DECORATORS = dict()

import sys
def register_decorator(cls):
    """Decorator to register plug-ins"""
    name = cls.channel_tag
    DECORATORS[name] = cls
    setattr(sys.modules[__name__], name, cls)
    return cls

class RegistryItem:
    def __init__(self, **attrs):
        self.handler = attrs["handler"]
        self.meta = attrs["meta"]
        self.channel_tag = attrs["channel_tag"]
        self.module = attrs["module"]
        self.doc = attrs["doc"]

class Channel:
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    channel_tag = "channel"

    decorator_kwargs = []
    decorator_required_kwargs = []

    _registry = []

    # def fmt_route(self):

    def __init__(self, **options):
        options = _.pick(options, *(self.decorator_kwargs))
        missed = [k for k in self.decorator_required_kwargs if k not in options.keys()]
        if len(missed) > 0:
            raise TypeError("Decorator {} - required args missed: {}".format(self.__class__.__name__, ",".join(missed)))
        self.options = options
        log.debug('Decorator: %s', self)
    
    def __str__(self):
        return self.channel_tag

    def __call__(self, handler):
        self._registry += [RegistryItem(
            handler=handler,
            meta=_.extend({}, self.options),
            channel_tag=self.channel_tag,
            module=handler.__module__,
            doc=handler.__doc__,
        )]
        log.debug('Decorator called: %s', self.channel_tag)
        return handler

    @classmethod
    def items(cls):
        if cls.__name__ == Channel.__name__:
            return iter(cls._registry)
        return _.filter(cls._registry, lambda v: v.channel_tag == cls.channel_tag)

    @classmethod
    def chain(cls):
        return _.chain(cls.items())



@register_decorator
class Cron(Channel):
    channel_tag = "cron"
    decorator_kwargs = ["seconds"]
    decorator_required_kwargs = []

    # def __init__(self, cron_factory):
    #     """Store "lazy" schedule factory:
    #     e.g.: lambda schedule: schedule.every(10).minutes
    #     Do not append final .do(job) here

    #     Upon instantiation, this object will be called with schedule.do(job) 
        
    #     Arguments:
    #         cron_factory {[type]} -- [description]
    #     """
    #     options = {
    #         "cron_factory": cron_factory,
    #     }
    #     super().__init__(**options)


@register_decorator
class Cli(Channel):
    channel_tag = "cli"


@register_decorator
class Http(Channel):
    channel_tag = "http"

    def as_routes(self):
        """Enum string routes with related handlers.

        Returns:
            [type] -- [description]
        """
        return _.map(self.items(), lambda rec: (
            f'/{rec.channel_tag}/{rec.module}.{rec.handler.__name__}',
            rec.handler
        ))


@register_decorator
class QA(Channel):
    channel_tag = "qa"

