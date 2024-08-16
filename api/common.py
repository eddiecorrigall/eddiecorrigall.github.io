import json

from datetime import datetime, timezone


def safe_serialize(obj):
    default = lambda o: f"<not-serialized: {type(o).__qualname__}>"
    return json.dumps(obj, default=default)


def datetime_now():
    return datetime.now(timezone.utc)

def to_timestamp(dt: datetime) -> int:
    return int(dt.timestamp())

def from_timestamp(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)
