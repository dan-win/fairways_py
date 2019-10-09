import os, sys, re
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
    if source is None:
        # force to load defaults:
        this.settings = {}
    elif isinstance(source, str):
        # Module name:
        dynload.import_module(source)
        this.settings = sys.modules[source]
    elif isinstance(source, types.ModuleType):
        this.settings = source
    elif isinstance(source, object):
        this.settings = source
    else:
        raise TypeError(f"conf.load cannot load settings from such type: '{source}'")

    # Replace env vars in values:
    
    # Load entrypoints:
    for record in ConfigHandler.items():
        handler = record.handler
        key = record.meta["config_key"]
        sub_conf = getattr(settings, key, None)
        try:
            handler(sub_conf)
        except Exception as e:
            log.error(f"Error during conf loading for {record.module}: {e!r}")


# SETTINGS_MODULE = os.environ["FAIRWAYS_PY_SETTINGS_MODULE"]

# dynload.import_module(SETTINGS_MODULE)

# settings = sys.modules[SETTINGS_MODULE]

RE_ENV_EXPRESSION = re.compile(r"\{\$(.*?)\}")

def replace_env_vars(s):
    """Replace all occurences of {$name} in string with values from os.environ
    
    Arguments:
        s {[str]} -- [description]
    
    Returns:
        [str] -- [String with replaced values]
    """
    def envrepl(match):
        (env_var,) = match.groups(1)
        return os.environ[env_var]

    return RE_ENV_EXPRESSION.sub(envrepl, s)

def parse_conf_nodes(settings_node):
    if isinstance(settings_node, dict):
        return ff.map(settings_node, lambda v, k: replace_env_vars(v) if isinstance(v, str) else v)
    raise TypeError("Types except dict are not supported now!")
    # if isinstance(settings_node, types.ModuleType):
    #     for attr_name in ff.filter(dir(settings_node), lambda name: not name.startswith("_")):
    #         att_val = getattr()
    # if isinstance(settings_node, (list, tuple)):
    #     for item in settings_node:
    #         if isinstance(item, str):
                
    
