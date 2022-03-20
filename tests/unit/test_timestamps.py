import time

from vial import timestamps

from tests import assertions


def test_epoch_millis() -> None:
    assertions.within_range(time.time() * 1000, timestamps.epoch_millis(), 10)
