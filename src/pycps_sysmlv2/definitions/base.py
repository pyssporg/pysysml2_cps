from __future__ import annotations
from dataclasses import dataclass, field

from ..parser_utils import json_dumps

from typing import Dict, Tuple, Optional, Set

@dataclass
class DefinitionBase:
    """Shared base for model objects with JSON debug rendering."""
    name: str = ""
    doc: Optional[str] = field(default=None, kw_only=True)

    def __str__(self) -> str:
        return json_dumps(self)

@dataclass
class DeclaredDefinition(DefinitionBase):
    """Generic declared artifact container with dynamic artifact kinds."""
    specializes: Optional[str] = None
    specializes_obj: Optional[object] = None
    source_file: Optional[str] = None

    artifact_kinds: Tuple[str, ...] = field(default_factory=tuple)
    items: Dict[str, Dict[str, object]] = field(default_factory=dict)

    # not utilized in resolved definitions
    redefines_items: Dict[str, Dict[str, object]] = field(default_factory=dict)
    remove_items: Dict[str, Set[str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for kind in self.artifact_kinds:
            self.items.setdefault(kind, {})
            self.redefines_items.setdefault(kind, {})
            self.remove_items.setdefault(kind, set())
