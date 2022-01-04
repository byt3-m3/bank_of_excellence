import logging

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

global_logger = logging.getLogger("GlobalLogger")
global_logger.setLevel(logging.INFO)
global_logger.addHandler(stream_handler)


def get_logger(name=__name__, level=logging.INFO):
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)

    _logger = logging.getLogger(name)
    _logger.setLevel(level)
    _logger.addHandler(stream_handler)
    return _logger


def get_global_logger():
    return global_logger
