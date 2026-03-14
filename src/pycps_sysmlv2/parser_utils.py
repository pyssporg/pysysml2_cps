"""Traceability Preamble
Template ID: PYCSYSML2_TRACE_PREAMBLE
Template Version: 1.1.0
Purpose: Shared utility helpers used by parser and model layers.
Design Notes:
- Keep helpers side-effect free so parsing behavior stays predictable in tests.
- Centralize JSON rendering rules used by repr/debug surfaces.
Key Invariants:
- json_dumps output must be stable for equivalent objects.
- Helpers should not import parser modules to avoid circular dependencies.
Strongly Connected External Modules:
- json
- dataclasses
Decision Log:
- Add dated, behavior-impacting decisions; avoid logging template-only edits.
"""
from __future__ import annotations

import json
import re
from enum import Enum
from pathlib import Path
from typing import Any, Tuple, List

def to_jsonable(value: Any, suppress_list : List[Any] | None) -> Any:
    if suppress_list is not None:
        if value in suppress_list:
            return "__ref__"

    # Variables
    if isinstance(value, dict):
        return {str(key): to_jsonable(val, suppress_list) for key, val in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [to_jsonable(item, suppress_list) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Enum):  # Must be first to not recurse into enum internals.
        return str(value.value)

    # Class
    if hasattr(value, "__dict__"):
        if suppress_list is not None:
            suppress_list.append(value)
        t = {"value_type": str(type(value))}
        return {**{str(key): to_jsonable(val, suppress_list) for key, val in vars(value).items()}, **t}

    return value


def json_dumps(value: Any, suppress_list = None) -> str:
    return json.dumps(to_jsonable(value, suppress_list), indent=2, sort_keys=True)


def collect_block(text: str, brace_start: int) -> Tuple[str, int]:
    """Return the substring inside the curly braces starting at brace_start."""
    depth = 0
    body_start = brace_start + 1
    idx = brace_start
    while idx < len(text):
        char = text[idx]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[body_start:idx], idx + 1
        idx += 1
    raise ValueError("Unterminated block while parsing SysML text")


def strip_inline_comment(line: str) -> str:
    result = line
    while "/*" in result and "*/" in result:
        start = result.find("/*")
        end = result.find("*/", start + 2)
        if end == -1:
            break
        result = (result[:start] + result[end + 2 :]).strip()
    return result.strip()


def normalize_doc(text: str) -> str:
    start = text.find("/*")
    end = text.rfind("*/")
    slice_ = text[start + 2 : end] if start != -1 and end != -1 else text
    return re.sub(r"\s+", " ", slice_.strip())
