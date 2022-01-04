from cbaxter1988_utils.log_utils import get_logger

logger = get_logger(__name__)


def log_invocation(func):
    def inner_func(*args, **kwargs):
        logger.info(f'Logging Function Execution: "{func.__name__}" Called With: (kwargs={kwargs})')
        return func(*args, **kwargs)

    return inner_func
