from http import HTTPStatus

from vial.app import Resource, Vial
from vial.gateway import Gateway
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


def test_teapot() -> None:
    response = Gateway(app).get("/teapot")
    assert response.status == HTTPStatus.IM_A_TEAPOT
    assert response.body == {"custom_message": "I really am a teapot"}


def test_confused_teapot() -> None:
    response = Gateway(app).get("/confused-teapot")
    assert response.status == HTTPStatus.BAD_GATEWAY
    assert response.body == {"custom_message": "I'm a really confused teapot"}
