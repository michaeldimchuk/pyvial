import json
import logging
import time
from logging import DEBUG, Handler, Logger, LogRecord
from typing import Any, cast
from unittest.mock import MagicMock

import pytest

from vial import timestamps
from vial.loggers import JsonFormatter

from tests import assertions


class CollectingHandler(Handler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.logs: list[str] = []

    def emit(self, record: LogRecord) -> None:
        self.logs.append(self.format(record))


@pytest.fixture(name="logger")
def logger_fixture(request: pytest.FixtureRequest) -> Logger:
    log = logging.getLogger(request.function.__name__)
    handler = CollectingHandler()
    handler.setFormatter(JsonFormatter())
    log.addHandler(handler)
    log.setLevel(DEBUG)
    return log


def test_format_time_default() -> None:
    formatter = JsonFormatter()
    record = MagicMock()
    record.created = 1656391930
    timestamp_format = "%Y-%m-%dT%H:%M:%S"
    timestamp = formatter.formatTime(record, timestamp_format)
    assert timestamp == time.strftime(timestamp_format, time.localtime(1656391930))


def test_log_normal(logger: Logger) -> None:
    logger.info("Hello world")

    record = _get_record(logger)
    _verify_log(record, "Hello world", "test_log_normal")


def test_log_exception(logger: Logger) -> None:
    try:
        raise ValueError("Oh no")
    except ValueError:
        logger.exception("That didn't go well")

    record = _get_record(logger)
    _verify_log(record, "That didn't go well", "test_log_exception")


def _get_record(logger: Logger) -> dict[str, str]:
    handler: CollectingHandler = cast(CollectingHandler, logger.handlers[0])
    assert len(handler.logs) == 1
    return dict(json.loads(handler.logs[0]))


def _verify_time(record: dict[str, str]) -> None:
    timestamp = timestamps.parse(record["time"])
    assertions.within_range(timestamp.timestamp() * 1000, timestamps.epoch_millis(), 10)


def _verify_log(record: dict[str, str], message: str, function: str) -> None:
    assert record["message"] == message
    assert record["name"] == function

    _verify_log_source(record, function)
    _verify_log_level(record)
    _verify_time(record)


def _verify_log_source(record: dict[str, str], function: str) -> None:
    module = __name__.rsplit(".", maxsplit=1)[-1]
    assert record["file"] == f"{module}.py"
    assert record["module"] == module
    assert record["function"] == function


def _verify_log_level(record: dict[str, str]) -> None:
    if traceback := record.get("traceback"):
        assert traceback.startswith("Traceback (most recent call last):")
        assert record["level"] == "ERROR"
    else:
        assert record["level"] == "INFO"
