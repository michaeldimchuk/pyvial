from datetime import datetime, timezone

from vial.exceptions import ServerError, VialError

DEFAULT_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def epoch_millis() -> float:
    return now().timestamp() * 1000


def now() -> datetime:
    return datetime.now(timezone.utc)


def parse(timestamp: str) -> datetime:
    return datetime.strptime(timestamp, DEFAULT_FORMAT).replace(tzinfo=timezone.utc)


def pretty(timestamp: datetime) -> str:
    if not (timestamp.tzinfo is None or timestamp.tzinfo == timezone.utc):
        raise ServerError(VialError.INVALID_TIMESTAMP_ZONE.get(timestamp.tzinfo))
    return timestamp.strftime(DEFAULT_FORMAT)


def of_epoch_seconds(seconds: float) -> datetime:
    return datetime.fromtimestamp(seconds, timezone.utc)
