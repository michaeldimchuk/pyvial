from vial.app import Vial

app = Vial(__name__)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "OK"}
