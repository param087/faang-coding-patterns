"""One harness for every template and solution module.

Writing 539 test files by hand would guarantee that some of them drift out of
sync with the page that embeds the code. Instead each module carries its own
cases and this file discovers them, so adding a solution automatically adds
its tests and a module with no cases is a hard failure rather than a silent
gap.

A module declares its cases one of two ways:

    CASES = [((arg1, arg2), expected), ...]   # with a module-level `solve`
    def check() -> None: ...                  # asserts internally

`check()` exists for the problems a single call cannot express: design
classes driven by an operation sequence, concurrency, and anything where the
answer is "any valid arrangement" and has to be verified rather than compared.
"""

from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Iterator
from types import ModuleType

import pytest


def _modules(package_name: str) -> Iterator[ModuleType]:
    package = importlib.import_module(package_name)
    for info in pkgutil.iter_modules(package.__path__):
        if info.name.startswith("_"):
            continue
        yield importlib.import_module(f"{package_name}.{info.name}")


def _ids(modules: list[ModuleType]) -> list[str]:
    return [m.__name__.split(".")[-1] for m in modules]


SOLUTIONS = list(_modules("solutions"))
TEMPLATES = list(_modules("code"))
ALL_MODULES = SOLUTIONS + TEMPLATES


@pytest.mark.parametrize("module", ALL_MODULES, ids=_ids(ALL_MODULES))
def test_module_declares_cases(module: ModuleType) -> None:
    """Every module must be testable — no silent coverage gaps."""
    has_cases = hasattr(module, "CASES") and hasattr(module, "solve")
    has_check = callable(getattr(module, "check", None))
    assert has_cases or has_check, (
        f"{module.__name__} declares neither CASES + solve() nor check()"
    )


@pytest.mark.parametrize("module", ALL_MODULES, ids=_ids(ALL_MODULES))
def test_module(module: ModuleType) -> None:
    check = getattr(module, "check", None)
    if callable(check):
        check()
        return

    cases = getattr(module, "CASES", None)
    solve = getattr(module, "solve", None)
    if cases is None or solve is None:
        pytest.skip("covered by test_module_declares_cases")

    assert cases, f"{module.__name__} has an empty CASES list"
    for index, (args, expected) in enumerate(cases):
        actual = solve(*args)
        assert actual == expected, (
            f"{module.__name__} case {index}: solve{args!r} "
            f"returned {actual!r}, expected {expected!r}"
        )
