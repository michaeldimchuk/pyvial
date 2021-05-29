import logging
from logging import Formatter, Logger, StreamHandler

DEFAULT_FORMAT = "[%(levelname)s] %(asctime)s %(filename)s.%(funcName)s: %(message)30s"


def new(name: str) -> Logger:
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    log.propagate = False
    log.addHandler(_get_handler())
    return log


def _get_handler() -> StreamHandler:
    handler = StreamHandler()
    handler.setFormatter(Formatter(DEFAULT_FORMAT))
    return handler
