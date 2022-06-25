# Vial
<p>
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
Basic `serverless.yml` file to deploy the project with the serverless framework:
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
The current request is tracked within a contextual object that wraps the lambda request. It can be accessed like so:
```
from vial import request
from vial.app import Vial
from vial.types import Request

app = Vial(__name__)


@app.get("/hello-world")
def hello_world() -> dict[str, list[str]]:
    request: Request = request.get()
    query_params = request.query_parameters
    if not query_params:
        raise ValueError("Must provide at least one query parameter")
    return dict(query_params)
```
The `request.get()` function is only available during a lambda request and will raise an error if called outside of one.

### Path Parameters
You can define path parameters like this:
```
@app.get("/users/{user_id}")
def get_user(user_id: str) -> User:
    return user_service.get(user_id)
```

Vial supports some path parameter parsing as part of the invocation process. For example when using a UUID
as a path parameter, Vial can convert it from a string to a UUID automatically:
```
from uuid import UUID

@app.get("/users/{user_id:uuid}")
def get_user(user_id: UUID) -> User:
    return user_service.get(user_id)
```

The following parsers are supported by default:

| Parser        | Type              |
| ------------- | ----------------- |
| `str`         | `str`             |
| `bool`        | `bool`            |
| `int`         | `int`             |
| `float`       | `float`           |
| `decimal`     | `decimal.Decimal` |
| `uuid`        | `uuid.UUID`       |

You can register your own parser like this:
```
@app.parser("list")
def list_parser(value: str) -> list[str]:
    return [value]


@app.get("/users/{user_id:list}")
def get_user(user_ids: list[str]) -> list[User]:
    return [user_service.get(user_id) for user_id in user_ids]
```
As parsers are bound directly to the registered route function, they have to be defined before the route
function that uses one is registered.

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
A test case with this example is available in `tests/samples/test_with_resources.py`.

## Middleware
You can register middleware functions to be executed before / after route invocations. All middleware is scoped to
where it's registered. A middleware function registered with the `Vial` instance is scoped to all routes within
the application, but a function registered with a `Resource` instance will only be invoked for routes defined in
that specific resource.

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
A test case with this example is available in `tests/samples/test_with_middleware.py`.


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
A test case with this example is available in `tests/samples/test_with_json_encoding.py`.

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
from vial.errors import BadRequestError
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
    response = gateway.post("/stores/my-cool-store", app.json.dumps({"store_name": "My very cool store"}))
    assert response.status == HTTPStatus.OK
    assert response.body == {"store_id": "my-cool-store", "store_name": "My very cool store"}
```
This code is also available in `tests/samples/test_with_gateway.py`.
