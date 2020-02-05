"""Entrypoint is a function which should handle some kind of external "requests" (different ways of invocation for your application). 
You can define different entrypoins in one module and associate some specific data with it.
Example (not functional here, for illustaration purposes only):

>>> # You can invoke this function running "python <yourappname> -c migrate":
>>> @entrypoint.cli(param="migrate")
>>> # Later in the "main" part of module we should call entrypoint.cmd.run() to run all registered entrypoins...
... def make_migration(): pass
>>> @amqp.consumer(queue="myqueue")
... def my_counsumer(): pass
>>> # Later in the "main" part of module we should call amqp.consumer.run() to run all registered entrypoins (or use its async counterpart: amqp.consumer.create_tasks_future())...

Generally, we can define multiple entrypoins per one module. """

from .entities import (Mark, RegistryItem, register_decorator)
from ..funcflow import FuncFlow as ff

import logging
log = logging.getLogger(__name__)

import functools

from abc import abstractmethod

import sys
import argparse

class EntrypointRegistryItem(RegistryItem):
    """Internal container to keep data related to single entrypoint """

    @property
    def handler(self):
        """Wrapped function
        
        :return: Decorated function which becomes handler for associated entrypoint
        :rtype: Callable
        """
        return self.subject

    def __str__(self):
        return f"Entrypoint: '{self.module}:{self.mark_name}' in function: '{self.handler.__name__}'"
    
    @classmethod
    @abstractmethod
    def run(self, args=None):
        """Invoke all functions decorated by this type of entrypoint.
        
        :param args: Some data to init run, defaults to None
        :type args: Any, optional
        """
        pass

class Channel(Mark):
    mark_name = "channel"

    registry_item_class = EntrypointRegistryItem


@register_decorator
class Cron(Channel):
    mark_name = "cron"
    decorator_kwargs = ["seconds"]
    decorator_required_kwargs = []


@register_decorator
class Cli(Channel):
    mark_name = "cli"
    decorator_kwargs = []
    decorator_required_kwargs = []


@register_decorator
class Cmd(Channel):
    """Invocation via terminal.
    Special "param" allows to run selected function only when you provide \-c / \--command argument while starting application.
    """
    mark_name = "cmd"
    decorator_kwargs = ["param"]
    decorator_required_kwargs = []
    description = "Run command by args"
    once_per_module = False

    @classmethod
    def run(cls, args=None):
        # TODO: add children parsers to parse context arguments (with displaying help also)
        def run_item(entrypoint_item):
            pass
        
        args = args or sys.argv[1:]
        parser = argparse.ArgumentParser()
        parser.add_argument('-c',  '--command', help='Select entrypoint by command param')
        # parser.add_argument('-f',  '--file', help='File with initial data')
        args = parser.parse_args(args)
        command = args.command
        print("COMMAND FOUND", command)

        item_to_run = cls.chain().find(lambda item: item.meta.get("param") == command).value
        if not item_to_run:
            log.debug("Cmd decorator: no entrypoints for -c param %s", command)
            return
            # raise ValueError(f"Cannot find entrypoint by param: {command}")
        return item_to_run.handler({})


class Listener(Channel):

    @classmethod
    def asgi_factory(cls):
        pass

    @classmethod
    def run(cls, args=None):
        raise NotImplementedError()

class Transmitter(Channel):

    @classmethod
    def run(cls, args=None):
        raise NotImplementedError()


@register_decorator
class QA(Channel):
    mark_name = "qa"


@register_decorator
class Http(Channel):
    mark_name = "http"

    def as_routes(self):
        """Enum string routes with related handlers.

        Returns:
            [type] -- [description]
        """
        return ff.map(self.items(), lambda rec: (
            f'/{rec.mark_name}/{rec.module}.{rec.handler.__name__}',
            rec.handler
        ))



@register_decorator
class ConfigHandler(Channel):
    mark_name = "conf"
    decorator_kwargs = ["config_key"]
    decorator_required_kwargs = ["config_key"]

    # Sometimes we need to use several config keys in one module:
    once_per_module = False

