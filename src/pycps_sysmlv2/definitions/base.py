from __future__ import annotations
from dataclasses import dataclass, field

import warnings
from ..parser_utils import json_dumps

from typing import Dict, Tuple, Optional, Set, ClassVar, Any


@dataclass
class SysMLBase:
    """Shared base for model objects with JSON debug rendering."""

    name: str = ""
    doc: Optional[str] = field(default=None, kw_only=True)
    parent: SysMLBase = None
    
    source_file: Optional[str] = None

    def __str__(self) -> str:
        return json_dumps(self)
    

@dataclass
class DefinitionBase(SysMLBase):
    DEFINITION_KINDS: ClassVar[tuple[str, ...]] = (
        "attributes",
        "parts",
        "ports",
        "requirements",
        "connections",
    )
    REFERENCE_KINDS: ClassVar[tuple[str, ...]] = (
        "parts",
        "ports",
        "requirements",
    )

    references: dict[str, dict[str, SysMLBase]] = field(
        default_factory=lambda: {k: {} for k in DefinitionBase.REFERENCE_KINDS}
    )
    definitions: dict[str, dict[str, SysMLBase]] = field(
        default_factory=lambda: {k: {} for k in DefinitionBase.DEFINITION_KINDS}
    )

    def _bucket(self, store: dict[str, dict[str, SysMLBase]], kind: str) -> dict[str, SysMLBase]:
        try:
            return store[kind]
        except KeyError as e:
            raise KeyError(f"Unknown kind: {kind}") from e

    def add_ref(
        self, kind: str, name: str, obj: SysMLBase, overwrite_warning: bool = True
    ) -> None:
        bucket = self._bucket(self.references, kind)
        if name in bucket and overwrite_warning:
            warnings.warn(
                f"Overwriting existing {kind} reference: {name}", stacklevel=2
            )
        bucket[name] = obj

    def remove_ref(self, kind: str, name: str) -> SysMLBase:
        return self._bucket(self.references, kind).pop(name)

    def add_def(
        self, kind: str, name: str, obj: SysMLBase, overwrite_warning: bool = True
    ) -> None:
        bucket = self._bucket(self.definitions, kind)
        if name in bucket and overwrite_warning:
            warnings.warn(
                f"Overwriting existing {kind} definition: {name}", stacklevel=2
            )
        bucket[name] = obj

    def remove_def(self, kind: str, name: str) -> SysMLBase:
        return self._bucket(self.definitions, kind).pop(name)

    def find_definition(self, kind: str, name: str):
        namespace = self
        while namespace is not None:
            for n, item in self._bucket(namespace.definitions, kind).items():
                if item.name == name:
                    return item
            namespace = namespace.parent


@dataclass
class InherenceDefinition(DefinitionBase):
    """Generic declared artifact container with dynamic artifact kinds."""

    specializes: Optional[str] = None
    specializes_obj: Optional[object] = None

    redefines_references: Dict[str, Dict[str, object]] = field(
        default_factory=lambda: {k: {} for k in DefinitionBase.REFERENCE_KINDS}
    )
    remove_references: Dict[str, Set[str]] = field(
        default_factory=lambda: {set() for k in DefinitionBase.REFERENCE_KINDS}
    )
