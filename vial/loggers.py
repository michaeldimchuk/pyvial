from __future__ import annotations

import json
import logging
from logging import Formatter, Handler, Logger, LogRecord, StreamHandler

from vial import timestamps


class LoggerFactory:

    DEFAULT_FORMAT = "[%(levelname)s] %(asctime)s %(filename)s.%(funcName)s: %(message)s"

    @classmethod
    def get(cls, name: str) -> Logger:
        log = logging.getLogger(name)
        log.setLevel(logging.DEBUG)
        log.propagate = False
        log.addHandler(cls.get_handler())
        return log

    @classmethod
    def get_handler(cls) -> Handler:
        handler = StreamHandler()
        handler.setFormatter(Formatter(cls.DEFAULT_FORMAT))
        return handler


class JsonFormatter(Formatter):
    def format(self, record: LogRecord) -> str:
        json_record = self.to_record(record)
        self.add_traceback(record, json_record)
        # Need to use the json provided by Vial
        return json.dumps(json_record)

    def add_traceback(self, record: LogRecord, json_record: dict[str, str]) -> None:
        if record.exc_info:
            json_record["traceback"] = self.formatException(record.exc_info)

    def formatTime(self, record: LogRecord, datefmt: str | None = None) -> str:
        if datefmt:
            return super().formatTime(record, datefmt)
        return timestamps.pretty(timestamps.of_epoch_seconds(record.created))

    def to_record(self, record: LogRecord) -> dict[str, str]:
        return {
            "message": record.getMessage(),
            "name": record.name,
            "level": record.levelname,
            "file": record.filename,
            "module": record.module,
            "function": record.funcName,
            "time": self.formatTime(record),
        }


class JsonLoggerFactory(LoggerFactory):
    @classmethod
    def get_handler(cls) -> Handler:
        handler = StreamHandler()
        handler.setFormatter(JsonFormatter())
        return handler
