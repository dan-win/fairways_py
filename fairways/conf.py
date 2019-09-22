import os, sys
from . import dynload

SETTINGS_MODULE = os.environ["FAIRWAYS_PY_SETTINGS_MODULE"]

dynload.import_module(SETTINGS_MODULE)

settings = sys.modules[SETTINGS_MODULE]

