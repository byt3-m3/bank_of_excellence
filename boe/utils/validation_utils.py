from datetime import datetime


def is_isodate_format_string(date_str):
    try:
        _ = datetime.fromisoformat(date_str)
        return True
    except ValueError:
        return False
