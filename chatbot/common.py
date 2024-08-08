import json


def safe_serialize(obj):
    default = lambda o: f"<not-serialized: {type(o).__qualname__}>"
    return json.dumps(obj, default=default)
