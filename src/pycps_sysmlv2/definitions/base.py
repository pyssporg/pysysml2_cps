from __future__ import annotations
from dataclasses import dataclass, field

from ..parser_utils import json_dumps

from typing import Dict, Tuple, Optional, Set

@dataclass
class SysMLBase:
    """Shared base for model objects with JSON debug rendering."""
    name: str = ""
    doc: Optional[str] = field(default=None, kw_only=True)
    source_file: Optional[str] = None

    def __str__(self) -> str:
        return json_dumps(self)


@dataclass
class DefinitionBase(SysMLBase):
    definition_kinds: Tuple[str, ...] = field(default_factory=tuple)
    reference_kinds: Tuple[str, ...] = field(default_factory=tuple)

    references: Dict[str, Dict[str, object]] = field(default_factory=dict)
    definitions: Dict[str, Dict[str, object]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for kind in self.reference_kinds:
            self.references.setdefault(kind, {})
        for kind in self.definition_kinds:
            self.definitions.setdefault(kind, {})


@dataclass
class InherenceDefinition(DefinitionBase):
    """Generic declared artifact container with dynamic artifact kinds."""
    specializes: Optional[str] = None
    specializes_obj: Optional[object] = None

    redefines_references: Dict[str, Dict[str, object]] = field(default_factory=dict)
    remove_references: Dict[str, Set[str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        super().__post_init__()
        for kind in self.reference_kinds:
            self.redefines_references.setdefault(kind, {})
            self.remove_references.setdefault(kind, set())
