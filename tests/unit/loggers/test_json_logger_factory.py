from logging import StreamHandler

from vial.loggers import JsonFormatter, JsonLoggerFactory


def test_get_handler() -> None:
    handler = JsonLoggerFactory.get_handler()
    assert isinstance(handler, StreamHandler)
    assert isinstance(handler.formatter, JsonFormatter)
