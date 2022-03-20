from typing import Union


def within_range(first: Union[int, float], second: Union[int, float], limit: int) -> None:
    error = f"Expected {first} to be within {limit} of {second}, but was {abs(first - second)}"
    assert abs(first - second) <= limit, error
