from typing import Mapping

from vial.app import Vial

from tests.application.user_blueprint import app as user_app

app = Vial()

app.register_blueprint(user_app)


@app.get("/health")
def health() -> Mapping[str, str]:
    return {"status": "OK"}
