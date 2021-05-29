from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Callable, Dict, List, Mapping, Tuple, Union
from uuid import UUID

from vial.types import HTTPMethod

_PARSERS = {"str": str, "bool": bool, "int": int, "float": float, "decimal": Decimal, "uuid": UUID}

Parser = Callable[[str], Union[str, bool, int, float, Decimal, UUID]]


@dataclass
class Route:
    path: str
    original_path: str
    method: HTTPMethod
    variables: Mapping[str, Callable[[str], Any]]
    function: Callable[..., Any]
    metadata: Mapping[str, Any]


def build(path: str, method: HTTPMethod, function: Callable[..., Any], metadata: Mapping[str, Any]) -> Route:
    components = path.split("/")
    parsed_components: List[str] = []
    variables: Dict[str, Parser] = {}
    for component in components:
        if component.startswith("{") and component.endswith("}"):
            name, parser = _build_variable(component)
            variables[name] = parser
            parsed_components.append(f"{{{name}}}")
        else:
            parsed_components.append(component)
    return Route("/".join(parsed_components), path, method, variables, function, metadata)


def _build_variable(component: str) -> Tuple[str, Parser]:
    placeholder = component[1:-1]
    name_and_parser = placeholder.split(":")
    if len(name_and_parser) == 1:
        return name_and_parser[0], str
    parser = _PARSERS.get(name_and_parser[1])
    if not parser:
        raise ValueError(f"No parser for '{name_and_parser[1]}' was registered")
    return name_and_parser[0], parser
