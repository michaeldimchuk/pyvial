import pytest

from vial.types import LambdaContext


@pytest.fixture
def context() -> LambdaContext:
    return LambdaContext("vial-test", "1", "arn:vial-test", 128, "1", "vial-test-log", "vial-test-log")
