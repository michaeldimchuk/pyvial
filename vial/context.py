import os


def is_deployed() -> bool:
    return bool(os.getenv("AWS_EXECUTION_ENV"))
