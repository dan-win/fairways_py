# -*- coding: utf-8 -*-
import json

# Heler to overcome json error on dates (receipt source: https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable):

from datetime import date, datetime

def _json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def serialize_json(data):
    return json.dumps(data, ensure_ascii=False, default=_json_serial)

def deserialize_json(s):
    return json.loads(s.decode('utf-8'))

def json_stream(fpath):
    def wrapper(data):
        with open(fpath, 'w') as f:
            f.write(json.dumps(data, ensure_ascii=False, default=_json_serial))
    return wrapper

class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name
        return json.JSONEncoder.default(self, obj)