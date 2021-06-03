import logging
from logging import Formatter, Logger, StreamHandler


class LoggerFactory:

    DEFAULT_FORMAT = "[%(levelname)s] %(asctime)s %(filename)s.%(funcName)s: %(message)30s"

    @classmethod
    def get(cls, name: str) -> Logger:
        log = logging.getLogger(name)
        log.setLevel(logging.DEBUG)
        log.propagate = False
        log.addHandler(cls.get_handler())
        return log

    @classmethod
    def get_handler(cls) -> StreamHandler:
        handler = StreamHandler()
        handler.setFormatter(Formatter(cls.DEFAULT_FORMAT))
        return handler
