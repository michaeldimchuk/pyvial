import json
import os
from typing import Any, Callable, TextIO, cast

from vial.types import T


def read(path: str) -> T:
    if path.startswith("/"):
        raise ValueError(f"Path may not start with '/': {path}")
    return _get_file(os.path.join(_find_root(), path))


def _get_file(path: str) -> T:
    if not os.path.exists(path):
        raise ValueError(f"File {path} does not exist")
    with open(path, encoding="utf-8") as file:
        return _parse(file)


def _parse(file: TextIO) -> T:
    _, extension = os.path.splitext(file.name)

    def default_parser(data: TextIO) -> str:
        return data.read()

    return cast(T, _get_parsers().get(extension[1:].lower(), default_parser)(file))


def _get_parsers() -> dict[str, Callable[[TextIO], Any]]:
    return {"json": lambda file: json.loads(file.read())}


def _find_root() -> str:
    root = os.getcwd()
    if index := root.find("tests") > 0:
        root = root[0:index]
    return f"{root}/tests/resources/"
