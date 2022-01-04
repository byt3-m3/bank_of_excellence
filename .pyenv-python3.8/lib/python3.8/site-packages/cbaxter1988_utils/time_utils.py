from datetime import datetime


def get_utc_timestamp() -> float:
    return datetime.utcnow().timestamp()


def get_now():
    _now = datetime.now()
    return f'{_now.month}-{_now.day}-{_now.year} {_now.hour}:{_now.minute}::{_now.second}'
