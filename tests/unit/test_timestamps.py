import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from vial import timestamps
from vial.exceptions import ServerError, VialError

from tests import assertions


def test_epoch_millis() -> None:
    assertions.within_range(time.time() * 1000, timestamps.epoch_millis(), 10)


def test_of_epoch_seconds() -> None:
    seconds = 1656391930.749801
    timestamp = timestamps.of_epoch_seconds(seconds)
    assert timestamp == datetime(2022, 6, 28, 4, 52, 10, 749801, tzinfo=timezone.utc)


def test_pretty() -> None:
    timestamp = datetime(2022, 6, 28, 4, 52, 10, 749801, tzinfo=timezone.utc)
    assert timestamps.pretty(timestamp) == "2022-06-28T04:52:10.749801Z"


def test_pretty_non_utc_timestamp() -> None:
    invalid_timezone = datetime.now(timezone.utc).astimezone(ZoneInfo("America/Los_Angeles")).tzinfo
    timestamp = datetime(2022, 6, 28, 4, 52, 10, 749801, tzinfo=invalid_timezone)
    cause = pytest.raises(ServerError, timestamps.pretty, timestamp)
    assert cause.value.error.code == VialError.INVALID_TIMESTAMP_ZONE.name
