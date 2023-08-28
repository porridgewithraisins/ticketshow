import inspect
from types import ModuleType
from typing import Any, Dict

from pydantic import ValidationError


def get_docs(module: ModuleType):
    md = module.__dict__
    mn = module.__name__
    docs = ""

    for name in md:
        if not inspect.isfunction(md[name]) or md[name].__module__ != mn:
            continue
        docs += md[name].__doc__ + "\n<br>\n"

    return docs[:-6]


def lookup(module: ModuleType, method: str):
    md = module.__dict__
    mn = module.__name__
    is_present = lambda: method in md
    is_not_imported = lambda: md[method].__module__ == mn
    is_a_function = lambda: inspect.isfunction(md[method])

    if is_present() and is_not_imported() and is_a_function():
        return md[method]
    return None


def validate(Model: Any, data: Any):
    try:
        validated = Model(**data)
        return validated.dict(), None
    except ValidationError as e:
        error: Dict[int | str, str] = {}
        for err in e.errors():
            for loc in err["loc"]:
                error[loc] = err["msg"]
        return None, error


def remove_symbols(input_str: str):
    cleaned_str = ""
    for char in input_str:
        if char.isalnum() or char.isspace():
            cleaned_str += char
    return cleaned_str
