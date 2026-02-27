from __future__ import annotations

from ..parser_utils import json_dumps

from typing import Dict, Tuple, Optional


class DefinitionBase:
    """Shared base for model objects with JSON debug rendering."""

    def __str__(self) -> str:
        return json_dumps(self)

class DeclaredDefinition(DefinitionBase):
    """Generic declared artifact container with dynamic artifact kinds."""

    source_file: Optional[str] = None
    
    artifact_kinds: Tuple[str, ...]
    items: Dict[str, Dict[str, object]]
    redefines_items: Dict[str, Dict[str, object]]
    remove_items: Dict[str, set[str]]

    def _init_declared_maps(self) -> None:
        for kind in self.artifact_kinds:
            self.items.setdefault(kind, {})
            self.redefines_items.setdefault(kind, {})
            self.remove_items.setdefault(kind, set())
