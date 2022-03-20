import dataclasses
import json
from enum import Enum
from json.encoder import JSONEncoder
from typing import Any, Callable, Protocol, Type
from uuid import UUID


class Json(Protocol):
    @staticmethod
    def dumps(value: Any) -> str:
        pass

    @staticmethod
    def loads(value: str) -> Any:
        pass


def _enum_to_string(value: Enum) -> str:
    return value.name


def _instance_check(class_: Type[Any]) -> Callable[[Any], bool]:
    def instance_checker(value: Any) -> bool:
        return isinstance(value, class_)

    return instance_checker


class DefaultEncoder(JSONEncoder):
    ENCODERS: list[tuple[Callable[[Any], bool], Callable[[Any], Any]]] = [
        (_instance_check(set), list),
        (_instance_check(UUID), str),
        (_instance_check(Enum), _enum_to_string),
        (dataclasses.is_dataclass, dataclasses.asdict),
    ]

    def default(self, o: Any) -> Any:
        for type_matcher, encoder in self.ENCODERS:
            if type_matcher(o):
                return encoder(o)
        return super().default(o)


class NativeJson(Json):
    @staticmethod
    def dumps(value: Any) -> str:
        return json.dumps(value, cls=DefaultEncoder)

    @staticmethod
    def loads(value: str) -> Any:
        return json.loads(value)
