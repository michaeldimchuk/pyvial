from vial.types import LambdaContext


def test_get_remaining_time_in_millis(context: LambdaContext) -> None:
    assert context.get_remaining_time_in_millis() == 0
