from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Any, Optional

from .base import SysMLBase
from .types import SysMLType

@dataclass(kw_only=True)
class SysMLAttribute(SysMLBase):

    type: Optional[SysMLType]
    value: Optional[Any]

    def is_list(self):
        return isinstance(self.value, (list, tuple))

    def enumerator(self, start=0):
        v = self.value
        if not self.is_list():
            v = [v]
        return enumerate(v, start=start)

    @staticmethod
    def from_literal(name, value: Optional[str], doc: Optional[str] = None):
        value = SysMLAttribute._parse_literal(value)
        type = SysMLType.from_value(value)
        return SysMLAttribute(name=name, type=type, value=value, doc=doc)

    @staticmethod
    def _parse_literal(value: Optional[str]) -> Any:
        if value is None:
            return None

        text = value.strip()
        if not text:
            return None

        lowered = text.lower()
        if lowered in {"true", "false"}:
            return lowered == "true"

        try:
            return ast.literal_eval(text)
        except (ValueError, SyntaxError):
            pass

        return text

    def _get_item(item: Any):
        if isinstance(item, (list, tuple)):
            return next((i for i in item if i is not None), None)
        return item
