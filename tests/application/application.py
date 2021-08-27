from http import HTTPStatus
from typing import List, Mapping, Union

from vial import request
from vial.app import Vial
from vial.middleware import CallChain
from vial.types import Request, Response

from tests.application.exceptions import CustomForbiddenError, CustomUnauthorizedError
from tests.application.user_resource import app as user_app

app = Vial(__name__)

app.register_resource(user_app)


@app.middleware
def log_events(event: Request, chain: CallChain) -> Response:
    app.logger.info("Began execution of %s", event.context)
    try:
        response = chain(event)
        response.headers["logged"] = "middleware-executed"
        return response
    finally:
        app.logger.info("Completed execution of %s", event.context)


@app.error_handler(CustomUnauthorizedError, CustomForbiddenError)
def custom_error_handler(error: Union[CustomUnauthorizedError, CustomForbiddenError]) -> Response:
    status = HTTPStatus.UNAUTHORIZED if isinstance(error, CustomUnauthorizedError) else HTTPStatus.FORBIDDEN
    return Response({"message": str(error)}, status=status)


@app.get("/health")
def health() -> Mapping[str, str]:
    return {"status": "OK"}


@app.get("/query-params-test")
def get_query_params() -> Mapping[str, List[str]]:
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
