import os


def get_env_strict(key):
    """
    Gets the eviornment variable based on the key, Raise KeyError in env var is invalid.
    :param key: enviornment variable
    :return:
    """
    try:
        return os.environ[key]
    except KeyError:
        print(f"Environment Variable: '{key}' Not Set ")
        if raise_exception:
            raise KeyError(f"Environment Variable: '{key}' Not Set")


def get_env(key, default_value=None):
    """
    Gets the eviornment variable based on the key, returns default value if key is not found

    :param key:
    :param default_value:
    :return:
    """
    return os.getenv(key, default_value)

def set_env(key, val):
    """
    Sets the env var to the val.

    :param key:
    :param val:
    :return:
    """
    os.putenv(key, val)