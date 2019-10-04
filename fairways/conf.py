import os, sys
import types

from fairways.decorators.entrypoint import ConfigHandler
from fairways.funcflow import FuncFlow as ff

from . import dynload

import logging
log = logging.getLogger()

settings = None

# this is a pointer to the module object instance itself.
this = sys.modules[__name__]

def load(source):
    if isinstance(source, str):
        # Module name:
        dynload.import_module(source)
        this.settings = sys.modules[source]
    elif isinstance(source, types.ModuleType):
        this.settings = source
    elif isinstance(source, object):
        this.settings = source
    else:
        raise TypeError(f"conf.load cannot load settings from such type: '{source}'")
    
    # Load entrypoints:
    for record in ConfigHandler.items():
        handler = record.handler
        key = record.meta["config_key"]
        sub_conf = getattr(settings, key)
        try:
            handler(sub_conf)
        except Exception as e:
            log.error(f"Error during conf loading for {record.module}: {e!r}")


# SETTINGS_MODULE = os.environ["FAIRWAYS_PY_SETTINGS_MODULE"]

# dynload.import_module(SETTINGS_MODULE)

# settings = sys.modules[SETTINGS_MODULE]

