from __future__ import annotations
from dataclasses import dataclass, field

from enum import Enum
import warnings
from ..parser_utils import json_dumps

from typing import Dict, Optional, Set


class NodeType(str, Enum):
    Attribute = "Attribute"
    Part = "Part"
    Port = "Port"
    Requirement = "Requirement"
    Connection = "Connection"


@dataclass
class SysMLBase:
    """Shared base for model objects with JSON debug rendering."""

    name: Optional[str] = ""
    type: str = ""
    doc: Optional[str] = field(default=None, kw_only=True)
    parent: Optional["SysMLBase"] = None

    source_file: Optional[str] = None

    def __str__(self) -> str:
        return json_dumps(self)


@dataclass
class DefinitionBase(SysMLBase):
    # These should be empty to let subclasses specify their own types
    DEF_KINDS: tuple[NodeType, ...] = tuple()
    REF_KINDS: tuple[NodeType, ...] = tuple()

    # Only internal, remove legacy references elsewhere
    _refs: dict[NodeType, dict[str, ReferenceBase]] = field(default_factory=dict)
    _defs: dict[NodeType, dict[str, DefinitionBase]] = field(default_factory=dict)

    def defs(self, type: NodeType):
        if type in self.DEF_KINDS:
            return self._defs.setdefault(type, {})
        else:
            raise KeyError(f"Unsupported def type ({type}) for container. ")

    def refs(self, type: NodeType):
        if type in self.REF_KINDS:
            return self._refs.setdefault(type, {})
        else:
            raise KeyError(f"Unsupported ref type ({type}) for container. ")

    def add_ref(
        self, type: NodeType, key: str, obj: SysMLBase, overwrite_warning: bool = True
    ) -> None:
        refs = DefinitionBase.refs(self, type)
        if key in refs and overwrite_warning:
            warnings.warn(f"Overwriting existing reference: {key}", stacklevel=2)
        refs[key] = obj

    def add_def(
        self, type: NodeType, key: str, obj: SysMLBase, overwrite_warning: bool = True
    ) -> None:
        defs = DefinitionBase.defs(self, type)
        if key in defs and overwrite_warning:
            warnings.warn(f"Overwriting existing definition: {key}", stacklevel=2)
        defs[key] = obj

    def remove_ref(self, type: NodeType, key: str) -> None:
        refs = DefinitionBase.refs(self, type)
        refs.pop(key)

    def remove_def(self, type: NodeType, key: str) -> None:
        defs = DefinitionBase.defs(self, type)
        defs.pop(key)

    def get_ref(self, type: NodeType, key: str) -> ReferenceBase:
        refs = self.refs(type)
        if key not in refs:
            raise KeyError(f"Key not found: {key}")
        return refs[key]

    def get_def(self, type: NodeType, key: str) -> DefinitionBase:
        """Should fetch all namespaces for definitions above as well"""
        namespace = self
        while namespace is not None:
            defs = namespace.defs(type)

            for def_key, item in defs.items():
                if def_key == key:
                    return item
            namespace = namespace.parent
        raise KeyError(f"Definition not found in namespace: Key:{key}")


@dataclass
class ReferenceBase(SysMLBase):
    ref_node: DefinitionBase = None  # Link to reference node


@dataclass
class InherenceDefinition(DefinitionBase):
    """Generic declared artifact container with dynamic artifact kinds."""

    specializes: Optional[str] = None
    specializes_obj: Optional[DefinitionBase] = None

    _redefine_refs: Dict[NodeType, Dict[str, ReferenceBase]] = field(default_factory=dict)
    _remove_refs: Dict[NodeType, Set[str]] = field(default_factory=dict)

    _redefine_defs: Dict[NodeType, Dict[str, DefinitionBase]] = field(default_factory=dict)
    _remove_defs: Dict[NodeType, Set[str]] = field(default_factory=dict)

    def redefine_refs(self, type: NodeType):
        if type in self.REF_KINDS:
            return self._redefine_refs.setdefault(type, {})
        else:
            raise KeyError(f"Unsupported item type ({type}) for container. ")

    def remove_refs(self, type: NodeType):
        if type in self.REF_KINDS:
            return self._remove_refs.setdefault(type, set())
        else:
            raise KeyError(f"Unsupported item type ({type}) for container. ")

    def redefine_defs(self, type: NodeType):
        if type in self.DEF_KINDS:
            return self._redefine_defs.setdefault(type, {})
        else:
            raise KeyError(f"Unsupported item type ({type}) for container. ")

    def remove_defs(self, type: NodeType):
        if type in self.DEF_KINDS:
            return self._remove_defs.setdefault(type, set())
        else:
            raise KeyError(f"Unsupported item type ({type}) for container. ")

    def defs(self, type: NodeType):
        return self._resolve_items(declared=super().defs(type), redefine=self.redefine_defs(type), remove=self.remove_defs(type))

    def refs(self, type: NodeType):
        return self._resolve_items(declared=super().refs(type), redefine=self.redefine_refs(type), remove=self.remove_refs(type))

    def _resolve_items(
        self,
        *,
        declared: Dict[str, SysMLBase],
        redefine: Dict[str, SysMLBase],
        remove: Set[str],
    ) -> Dict[str, object]:
        resolved = dict(declared)
        resolved.update(redefine)
        for key in remove:
            resolved.pop(key, None)
        return resolved
