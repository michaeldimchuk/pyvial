import os
from unittest.mock import patch

from vial import context


def test_is_deployed() -> None:
    assert not context.is_deployed()

    with patch.dict(os.environ, {"AWS_EXECUTION_ENV": "AWS_Lambda_python3.9"}):
        assert context.is_deployed()
