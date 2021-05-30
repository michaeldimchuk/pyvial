# Vial
A micro web framework for AWS Lambda.

## Installation
To add vial to your project, run the following command:
```
poetry add pyvial

# If you use pip, run this instead:

pip install pyvial
```

## Usage
### Entry Point
The main entry point of the application is always the `Vial#__call__` function. When deploying to AWS Lambda,
the Lambda handler should point to the `Vial` object in whichever file it's defined in. As an example:
```
from vial.app import Vial

app = Vial()
```
If this code snippet is defined in an `app.py` file, the handler would be `app.app`.

### Basic API
```
from typing import Mapping
from vial.app import Vial

app = Vial()


@app.get("/hello-world")
def hello_world() -> Mapping[str, str]:
    return {"hello": "world"}
```

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
def list_parser(value: str) -> List[str]:
    return [value]


@app.get("/users/{user_id:list}")
def get_user(user_ids: List[str]) -> User:
    return user_service.get(user_id)
```
As parsers are bound directly to the registered route function, they have to be defined before the route
function that uses one is registered.

## Json Encoding
You can customize how Vial serializes / deserializes JSON objects by passing a custom encoder. The below
example shows how to substitute the native JSON module with another library like `simplejson`:
```
import simplejson
from vial.app import Vial, Json


class SimpleJson(Json):
    @staticmethod
    def dumps(value: Any) -> str:
        return simplejson.dumps(value)

    @staticmethod
    def loads(value: str) -> Any:
        return simplejson.loads(value)

class JsonVial:
    json_class = SimpleJson


app = SimpleJsonVial()
```
