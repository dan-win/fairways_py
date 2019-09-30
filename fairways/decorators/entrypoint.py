"Special marks for module executables which plays some special role"

from .entities import (Mark, RegistryItem, register_decorator)
from ..funcflow import FuncFlow as ff

import logging
log = logging.getLogger(__name__)

import functools


class EntrypointRegistryItem(RegistryItem):

    @property
    def handler(self):
        return self.subject

    def __str__(self):
        return f"Entrypoint: '{self.module}:{self.mark_name}' in function: '{self.handler.__name__}'"

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
class QA(Channel):
    mark_name = "qa"

