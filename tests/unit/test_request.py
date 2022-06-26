import pytest

from vial import request
from vial.exceptions import ServerError
from vial.request import RequestContext
from vial.types import HTTPMethod, LambdaContext, MultiDict, Request

from tests import assertions


@pytest.fixture(name="http_request")
def http_request_fixture(context: LambdaContext) -> Request:
    return Request(
        {"hello": "world"}, context, HTTPMethod.GET, "/hello/world", "/hello/world", MultiDict(), MultiDict(), None
    )


def test_get(http_request: Request) -> None:
    with RequestContext(http_request):
        assert request.get() == http_request


def test_elapsed_time(http_request: Request) -> None:
    with RequestContext(http_request) as context:
        assert request.elapsed_time()
        assertions.within_range(request.elapsed_time(), context.elapsed_time, 10)


def test_remaining_time(http_request: Request) -> None:
    with RequestContext(http_request):
        assert request.remaining_time() == http_request.context.get_remaining_time_in_millis()


def test_get_no_active_request() -> None:
    pytest.raises(ServerError, request.get)
