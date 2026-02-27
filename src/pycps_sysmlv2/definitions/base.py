from __future__ import annotations

from ..parser_utils import json_dumps


class DefinitionBase:
    """Shared base for model objects with JSON debug rendering."""

    def __str__(self) -> str:
        return json_dumps(self)
