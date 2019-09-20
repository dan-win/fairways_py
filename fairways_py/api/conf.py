import os, sys
from . import dynload

import logging

log = logging.getLogger("app")

SETTINGS_MODULE = os.environ["FAIRWAYS_PY_SETTINGS_MODULE"]

log.debug(f"...Importing settings: {SETTINGS_MODULE}")

dynload.import_module(SETTINGS_MODULE)

settings = sys.modules[SETTINGS_MODULE]

