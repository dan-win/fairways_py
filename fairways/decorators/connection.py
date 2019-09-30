"Special marks for module executables which plays some special role"

from .entities import (Mark, RegistryItem, register_decorator)
from ..funcflow import FuncFlow as ff

import logging
log = logging.getLogger(__name__)


class ConnectionsRegistryItem(RegistryItem):

    @property
    def handler(self):
        return self.subject

    def __str__(self):
        return f"Connections: {self.module}:{self.mark_name} / function: {self.handler.__name__}"


@register_decorator
class DefineConnections(Mark):
    mark_name = "define"

    registry_item_class = ConnectionsRegistryItem

    decorator_kwargs = []
    decorator_required_kwargs = []
