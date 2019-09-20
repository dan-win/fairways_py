import sys

if sys.version_info < (3, 6):
    raise SystemError("This package requires Python version 3.6 or above")