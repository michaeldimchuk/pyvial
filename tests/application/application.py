from typing import List, Mapping

from vial import request
from vial.app import Vial
from vial.middleware import CallChain
from vial.types import Request, Response

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


@app.get("/health")
def health() -> Mapping[str, str]:
    return {"status": "OK"}


@app.get("/query-params-test")
def get_query_params() -> Mapping[str, List[str]]:
    return dict(request.get().query_parameters)
