from __future__ import annotations


def within_range(first: int | float, second: int | float, limit: int) -> None:
    error = f"Expected {first} to be within {limit} of {second}, but was {abs(first - second)}"
    assert abs(first - second) <= limit, error
