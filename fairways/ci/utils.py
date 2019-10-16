
import io
import csv

import logging
log = logging.getLogger(__name__)

def csv2py(s, typecast_fields=None):
    """
    Convert tab-delimited text with headers row to list if dicts.
    Emulate DB response for query
    """
    f = io.StringIO(s)
    py_obj = list(csv.DictReader(f, dialect="excel-tab"))
    if isinstance(typecast_fields, dict):
        for rec in py_obj:
            for name, value in rec.items():
                rule = typecast_fields.get(name)
                if  callable(rule):
                    try:
                        rec[name] = rule(value)
                    except Exception as e:
                        log.error("Error in csv2py: %s, %s", e, rec)
    return py_obj

def trace_middleware_factory(log):
    return TraceMiddleware(log)

class TraceMiddleware:

    def __init__(self, log):
        self.step = 1
        self.log = log

    def __call__(self, method, data, **kwargs):
        result = method(data)
        self.log.info("\nSTEP #{} [{}], data after:\n {!r}".format(self.step, method.__name__, result))
        self.step += 1
        return result
