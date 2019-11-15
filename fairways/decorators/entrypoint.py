"Special marks for module executables which plays some special role"

from .entities import (Mark, RegistryItem, register_decorator)
from ..funcflow import FuncFlow as ff

import logging
log = logging.getLogger(__name__)

import functools

from abc import abstractmethod

import sys
import argparse

class EntrypointRegistryItem(RegistryItem):

    @property
    def handler(self):
        return self.subject

    def __str__(self):
        return f"Entrypoint: '{self.module}:{self.mark_name}' in function: '{self.handler.__name__}'"
    
    @classmethod
    @abstractmethod
    def run(self, args=None):
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
    mark_name = "cmd"
    decorator_kwargs = ["param"]
    decorator_required_kwargs = []
    description = "Run command by args"
    once_per_module = False

    @classmethod
    def run(cls, args=None):
        def run_item(entrypoint_item):
            pass
        
        args = args or sys.argv
        parser = argparse.ArgumentParser()
        parser.add_argument('-c',  '--command', required=True, help='Select entrypoint by command param')
        args = parser.parse_args(args)
        command = args.command

        item_to_run = cls.chain().find(lambda item: item.meta.get("param") == command).value
        if not item_to_run:
            raise ValueError(f"Cannot find entrypoint by param: {command}")
        return item_to_run.handler()


class Listener(Channel):

    @classmethod
    def asgi_factory(cls):
        pass

    @classmethod
    def run(cls, args=None):
        def run_item(entrypoint_item):
            pass
        
        args = args or sys.argv
        parser = argparse.ArgumentParser()
        parser.add_argument('-c',  '--command', required=True, help='Select entrypoint by command param')
        args = parser.parse_args(args)
        command = args.command

        item_to_run = cls.chain().find(lambda item: item.meta.get("param") == command).value
        if not item_to_run:
            raise ValueError(f"Cannot find entrypoint by param: {command}")
        return item_to_run.handler()

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

