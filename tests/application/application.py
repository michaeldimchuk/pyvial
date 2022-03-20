import json
from http import HTTPStatus
from typing import Any, Union

from vial import request
from vial.app import Vial
from vial.middleware import CallChain
from vial.types import HTTPMethod, Request, Response

from tests.application.exceptions import CustomForbiddenError, CustomUnauthorizedError
from tests.application.user_resource import app as user_app

app = Vial(__name__)
app_without_middleware = Vial("no_middleware")

app.register_resource(user_app)


@app.middleware
def log_events(event: Request, chain: CallChain) -> Response:
    app.logger.info("Began execution of %s %s", event.method.name, event.path)
    try:
        response = chain(event)
        response.headers["logged"] = "middleware-executed"
        return response
    finally:
        app.logger.info("Completed execution of %s %s", event.method.name, event.path)


@app.parser("list")
def set_parser(value: str) -> list[str]:
    return list(value)


@app.error_handler(CustomUnauthorizedError, CustomForbiddenError)
def custom_error_handler(error: Union[CustomUnauthorizedError, CustomForbiddenError]) -> Response:
    status = HTTPStatus.UNAUTHORIZED if isinstance(error, CustomUnauthorizedError) else HTTPStatus.FORBIDDEN
    return Response({"message": str(error)}, status=status)


@app.get("/health")
@app_without_middleware.get("/health")
def health() -> dict[str, str]:
    return {"status": "OK"}


@app.get("/response-returned")
def response_returned() -> Response:
    return Response({"status": "OK"}, {"custom-header": "custom-value"}, HTTPStatus.ACCEPTED)


@app.get("/tuple-returned")
def tuple_returned() -> tuple[dict[str, str], dict[str, str], HTTPStatus]:
    return {"status": "OK"}, {"custom-header": "custom-value"}, HTTPStatus.OK


@app.get("/string-returned")
def string_returned() -> str:
    return json.dumps({"status": "OK"})


@app.get("/parser-type-returned/{some_variable:list}")
def parser_type_returned(some_variable: list[str]) -> dict[str, Any]:
    return {"type": str(type(some_variable)), "value": some_variable}


@app.get("/query-params-test")
def get_query_params() -> dict[str, list[str]]:
    return dict(request.get().query_parameters)


@app.get("/custom-forbiden-error")
def custom_forbidden_error() -> None:
    raise CustomForbiddenError("Very secret")


@app.get("/custom-unauthorized-error")
def custom_unauthorized_error() -> None:
    raise CustomUnauthorizedError("Learn to type passwords")


@app.get("/really-bad-error")
def really_bad_error() -> None:
    raise Exception("This can't happen")


@app.get("/method-test")
@app.post("/method-test")
@app.put("/method-test")
@app.patch("/method-test")
@app.delete("/method-test")
@app.route("/method-test", [HTTPMethod.OPTIONS, HTTPMethod.TRACE])
def return_method() -> dict[str, str]:
    return {"method": request.get().method.name}
