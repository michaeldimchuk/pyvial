# Vial
<p>
    <a href="https://pypi.org/project/pyvial/">
        <img src="https://badgen.net/pypi/v/pyvial" alt="Latest Version" style="max-width:100%;">
    </a>
    <a href="https://github.com/michaeldimchuk/pyvial/actions/workflows/tests.yaml">
        <img src="https://github.com/michaeldimchuk/pyvial/actions/workflows/tests.yaml/badge.svg" alt="Test Status" style="max-width:100%;">
    </a>
    <a href="https://github.com/pre-commit/pre-commit">
        <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white" alt="Pre-Commit Enabled" style="max-width:100%;">
    </a>
</p>

Vial is an unopinionated micro web framework for AWS Lambda. It's main purpose is to provide an easy to use
interface while also making the core functionality of the framework as modular as possible.

## Installation
To add vial to your project, run the following command:
```
poetry add pyvial
```

## Usage
### Entry Point
The main entry point of the application is always the `Vial#__call__` function. When deploying to AWS Lambda,
the Lambda handler should point to the `Vial` object in whichever file it's defined in. As an example:
```
from vial.app import Vial

app = Vial(__name__)
```
If this code snippet is defined in an `app.py` file, the handler would be `app.app`.

### Basic API
```
from vial.app import Vial

app = Vial(__name__)


@app.get("/hello-world")
def hello_world() -> dict[str, str]:
    return {"hello": "world"}
```
A test case with this example is available in [tests/samples/test_with_app.py](tests/samples/test_with_app.py).

Basic `serverless.yml` file to deploy the project with the [serverless framework](https://www.serverless.com/framework/docs/getting-started):
```
service: my-function
provider:
  name: aws
  runtime: python3.9
  memorySize: 128
  region: us-west-2

package:
  patterns:
    - app.py

functions:
  api:
    handler: app.app
    events:
      - http: get /hello-world

custom:
  pythonRequirements:
    usePoetry: true

plugins:
  - serverless-python-requirements
```
You can now deploy the project with `serverless deploy`.

### Current Request
The current request is tracked within a contextual object that wraps the lambda request, and can be accessed
through the `vial.request` module. The `request.get()` function is only available during a lambda request,
and will raise an error if called outside of one. It can be accessed like so:
```
from vial import request
from vial.app import Vial
from vial.types import Request

app = Vial(__name__)


@app.get("/hello-world")
def hello_world() -> dict[str, list[str]]:
    if not (query_params := request.get().query_parameters):
        raise ValueError("Must provide at least one query parameter")
    return dict(query_params)
```
A test case with this example is available in [tests/samples/test_with_current_request.py](tests/samples/test_with_current_request.py).

### Path Parameters
You can define path parameters like this:
```
from dataclasses import dataclass

from vial.app import Vial

app = Vial(__name__)


@dataclass
class User:
    user_id: str


@app.get("/users/{user_id}")
def get_user(user_id: str) -> User:
    return User(user_id)
```
A test case with this example is available in [tests/samples/test_with_path_parameters.py](tests/samples/test_with_path_parameters.py).

Vial supports some path parameter parsing as part of the invocation process. For example when using a UUID
as a path parameter, Vial can convert it from a string to a UUID automatically:
```
from dataclasses import dataclass
from uuid import UUID, uuid4

from vial.app import Vial

app = Vial(__name__)


@dataclass
class User:
    user_id: UUID


@app.get("/users/{user_id:uuid}")
def get_user(user_id: UUID) -> User:
    if not isinstance(user_id, UUID):
        raise AssertionError("Invalid input")
    return User(user_id)
```
A test case with this example is available in [tests/samples/test_with_parser.py](tests/samples/test_with_parser.py).

The following parsers are supported by default:

| Parser        | Type              |
| ------------- | ----------------- |
| `str`         | `str`             |
| `bool`        | `bool`            |
| `int`         | `int`             |
| `float`       | `float`           |
| `decimal`     | `decimal.Decimal` |
| `uuid`        | `uuid.UUID`       |

You can register your own parser that consumes a string variable and converts it to any other type.
As parsers are bound directly to the registered route function, they have to be defined before the route
function that uses one is registered.
```
@app.parser("list")
def list_parser(value: str) -> list[str]:
    return [value]


@app.get("/users/{user_ids:list}")
def get_users(user_ids: list[str]) -> list[User]:
    if not isinstance(user_ids, list) or len(user_ids) != 1:
        raise AssertionError("Invalid input")
    return list(map(User, user_ids))
```
A test case with this example is available in [tests/samples/test_with_custom_parser.py](tests/samples/test_with_custom_parser.py).

## Resources
As your application grows, you may want to split certain functionality amongst resources and files, similar to
blueprints of other popular frameworks like Flask.

You can define a resource like this:
```
from dataclasses import dataclass

from vial.app import Resource, Vial

stores_app = Resource(__name__)


@dataclass
class Store:
    store_id: str


@stores_app.get("/stores/{store_id}")
def get_store(store_id: str) -> Store:
    return Store(store_id)


app = Vial(__name__)

app.register_resource(stores_app)
```
A test case with this example is available in [tests/samples/test_with_resources.py](tests/samples/test_with_resources.py).

## Middleware
You can register middleware functions to be executed before / after route invocations. All middleware is scoped to
where it's registered. A middleware function registered with the `Vial` instance is scoped to all routes within
the application, but a function registered with a `Resource` instance will only be invoked for routes defined in
that specific resource.

The route invocation will be the last callable in the call chain, so any middleware in the chain before can
exit the request and prevent the route invocation or even any other middleware from being called, exiting instead.
This may be helpful in cases where an application needs to fail early if the request isn't valid, like if a
required header is missing.

Below is an example of registering a middleware to log route invocation:
```
from __future__ import annotations

from vial import request
from vial.app import Vial
from vial.middleware import CallChain
from vial.types import Request, Response

app = Vial(__name__)


@app.middleware
def log_events(event: Request, chain: CallChain) -> Response:
    app.logger.info("Began execution of %s", event.context)
    event.headers["custom-injected-header"] = "hello there"
    try:
        return chain(event)
    finally:
        app.logger.info("Completed execution of %s", event.context)


@app.get("/hello-world")
def hello_world() -> dict[str, str | list[str]]:
    return {"hello": "world", **request.get().headers}
```
A test case with this example is available in [tests/samples/test_with_middleware.py](tests/samples/test_with_middleware.py).


## Error Handling
When errors are raised by the application, the default error handler will iterate the class inheritance hierarchy of the
exception that was raised, trying to find the most fine grained error handler possible. Default error handlers for common
exception types like `Exception` or `ValueError` are provided, but can be overridden. Below is a sample on how to register
custom error handlers or override existing ones:
```
from http import HTTPStatus

from vial.app import Vial
from vial.gateway import Gateway
from vial.types import Response

app = Vial(__name__)


class CustomError(Exception):
    pass


class ConfusedError(CustomError):
    pass


@app.error_handler(CustomError)
def custom_error_handler(error: CustomError) -> Response:
    return Response({"custom_message": str(error)}, status=HTTPStatus.IM_A_TEAPOT)


@app.error_handler(ConfusedError)
def confused_error_handler(error: ConfusedError) -> Response:
    return Response({"custom_message": str(error)}, status=HTTPStatus.BAD_GATEWAY)


@app.get("/teapot")
def teapot() -> None:
    raise CustomError("I really am a teapot")


@app.get("/confused-teapot")
def confused_teapot() -> None:
    raise ConfusedError("I'm a really confused teapot")
```
A test case with this example is available in [tests/samples/test_with_error_handling.py](tests/samples/test_with_error_handling.py).

Error handlers are bound to the resource they were registered in, whether that's the global `Vial` application or
a specific `Resource` instance. When an error occurs in a route, the "owner" application / resource is taken into consideration when
choosing the error handler to use.

An error handler registered in a `Resource` will always have precedence over a global error handler registered in the `Vial`
application. This allows for resources to either override global error handling mechanisms or add customization for more
fine grained exception types.

Note that the most fine grained error handler is always chosen, no matter where it comes from. That means that in a scenario
like this:
```
class First(Exception):
    pass

class Second(First):
    pass

class Third(Second):
    pass
```
If the `Vial` application registers error handlers for `First` and `Third` while the `Resource` registers an override for
`Second`, then when an exception of type `Third` is thrown, the global error handler will be used because it has a closer
match to the exception, even if its parent is overridden in the `Resource`.

Below is an example of a `Resource` specific error handler:
```
from http import HTTPStatus

from vial.app import Resource, Vial
from vial.types import Response

app = Vial(__name__)

confused_app = Resource(f"confused_{__name__}")


class CustomError(Exception):
    pass


class ConfusedError(CustomError):
    pass


@app.error_handler(CustomError)
def custom_error_handler(error: CustomError) -> Response:
    return Response({"custom_message": str(error)}, status=HTTPStatus.IM_A_TEAPOT)


@confused_app.error_handler(ConfusedError)
def confused_error_handler(error: ConfusedError) -> Response:
    return Response({"custom_message": str(error)}, status=HTTPStatus.BAD_GATEWAY)


@app.get("/teapot")
def teapot() -> None:
    raise CustomError("I really am a teapot")


@confused_app.get("/confused-teapot")
def confused_teapot() -> None:
    raise ConfusedError("I'm a really confused teapot")


app.register_resource(confused_app)
```
A test case with this example is available in [tests/samples/test_with_resource_error_handling.py](tests/samples/test_with_resource_error_handling.py).


## Json Encoding
You can customize how Vial serializes / deserializes JSON objects by passing a custom encoder. The below
example shows how to substitute the native JSON module with another library like `simplejson`:
```
from decimal import Decimal
from typing import Any

import simplejson

from vial.app import Vial
from vial.json import Json


class SimpleJson(Json):
    @staticmethod
    def dumps(value: Any) -> str:
        return simplejson.dumps(value)

    @staticmethod
    def loads(value: str) -> Any:
        return simplejson.loads(value)


class SimpleJsonVial(Vial):
    json_class = SimpleJson


app = SimpleJsonVial(__name__)


@app.get("/prices")
def get_prices() -> dict[str, Decimal]:
    # Decimal is not supported natively by the json module, but is by simplejson.
    return {"bread": Decimal("42.24"), "cheese": Decimal("129.34")}
```
A test case with this example is available in [tests/samples/test_with_json_encoding.py](tests/samples/test_with_json_encoding.py).

## Testing
The `vial.gateway.Gateway` class provides functionality to interact with the Vial application locally,
without deploying to AWS Lambda. It can be constructed using the original `Vial` application instance,
exposing the application endpoints with basic URL path matching.

Here is an example test case using `pytest`:
```
from http import HTTPStatus

import pytest

from vial import request
from vial.app import Vial
from vial.exceptions import BadRequestError
from vial.gateway import Gateway

app = Vial(__name__)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "OK"}


@app.post("/stores/{store_id}")
def create_store(store_id: str) -> dict[str, str]:
    if not (body := request.get().body):
        raise BadRequestError("Bad request")
    return {"store_id": store_id, **app.json.loads(body)}


@pytest.fixture(name="gateway")
def gateway_fixture() -> Gateway:
    return Gateway(app)


def test_health(gateway: Gateway) -> None:
    response = gateway.get("/health")
    assert response.status == HTTPStatus.OK
    assert response.body == {"status": "OK"}


def test_create_store(gateway: Gateway) -> None:
    body = app.json.dumps({"store_name": "My cool store"})
    response = gateway.post("/stores/my-cool-store", body)
    assert response.status == HTTPStatus.OK
    assert response.body == {"store_id": "my-cool-store", "store_name": "My cool store"}
```
This code is also available in [tests/samples/test_with_gateway.py](tests/samples/test_with_gateway.py).
