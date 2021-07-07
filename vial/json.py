import json
from json.encoder import JSONEncoder
from typing import Any, Protocol


class Json(Protocol):
    @staticmethod
    def dumps(value: Any) -> str:
        pass

    @staticmethod
    def loads(value: str) -> Any:
        pass


class DefaultEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, set):
            return list(o)
        return super().default(o)


class NativeJson(Json):
    @staticmethod
    def dumps(value: Any) -> str:
        return json.dumps(value, cls=DefaultEncoder)

    @staticmethod
    def loads(value: str) -> Any:
        return json.loads(value)
