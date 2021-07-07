import pytest

from vial import request
from vial.errors import ServerError
from vial.request import RequestContext
from vial.types import HTTPMethod, LambdaContext, MultiDict, Request


def test_get(context: LambdaContext) -> None:
    http_request = Request(
        {"hello": "world"}, context, HTTPMethod.GET, "/hello/world", "/hello/world", MultiDict(), MultiDict(), None
    )
    with RequestContext(http_request):
        assert request.get() == http_request


def test_get_no_active_request() -> None:
    pytest.raises(ServerError, request.get)
