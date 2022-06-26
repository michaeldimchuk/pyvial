import pytest

from vial.exceptions import NotFoundError
from vial.gateway import RouteMatcher

from tests.application.application import app


@pytest.fixture(name="matcher")
def matcher_fixture() -> RouteMatcher:
    return RouteMatcher(list(app.routes))


def test_match_exact_no_path_params(matcher: RouteMatcher) -> None:
    match = matcher.match("/health")
    assert match.route == "/health"
    assert match.path_params == {}
    assert match.query_params == {}


def test_match_exact_no_path_params_trailing_slash(matcher: RouteMatcher) -> None:
    match = matcher.match("/health/")
    assert match.route == "/health"
    assert match.path_params == {}
    assert match.query_params == {}


def test_match_exact_no_path_params_has_query_params(matcher: RouteMatcher) -> None:
    match = matcher.match("/health?key=hello&value=world&values=hello&values=world")
    assert match.route == "/health"
    assert match.path_params == {}
    assert match.query_params == {"key": ["hello"], "value": ["world"], "values": ["hello", "world"]}


def test_match_exact_path_params(matcher: RouteMatcher) -> None:
    match = matcher.match("/path/hello/has/world/params")
    assert match.route == "/path/{key}/has/{value}/params"
    assert match.path_params == {"key": "hello", "value": "world"}
    assert match.query_params == {}


def test_match_no_route_available(matcher: RouteMatcher) -> None:
    pytest.raises(NotFoundError, matcher.match, "/this/is/a/very/fake/path/that/obviously/wont/get/matched")
