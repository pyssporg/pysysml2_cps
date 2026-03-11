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
    parent: SysMLBase = None

    source_file: Optional[str] = None

    def __str__(self) -> str:
        return json_dumps(self)


@dataclass
class DefinitionBase(SysMLBase):
    # These should be empty to let subclasses specify their own types
    DEF_KINDS: tuple[NodeType, ...] = tuple()
    REF_KINDS: tuple[NodeType, ...] = tuple()

    # Only internal, remove legacy references elsewhere
    _refs: dict[NodeType, dict[str, SysMLBase]] = field(default_factory=dict)
    _defs: dict[NodeType, dict[str, SysMLBase]] = field(default_factory=dict)

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
        refs = self.refs(type)
        if key in refs and overwrite_warning:
            warnings.warn(f"Overwriting existing reference: {key}", stacklevel=2)
        refs[key] = obj

    def add_def(
        self, type: NodeType, key: str, obj: SysMLBase, overwrite_warning: bool = True
    ) -> None:
        defs = self.defs(type)
        if key in defs and overwrite_warning:
            warnings.warn(f"Overwriting existing definition: {key}", stacklevel=2)
        defs[key] = obj

    def remove_ref(self, type: NodeType, key: str) -> None:
        refs = self.refs(type)
        refs.pop(key)

    def remove_def(self, type: NodeType, key: str) -> None:
        defs = self.defs(type)
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

    specializes: Optional[DefinitionBase] = None

    _redefine_references: Dict[NodeType, Dict[str, object]] = field(default_factory=dict)
    # Should be a set, removing something does not necessitate an object
    _remove_references: Dict[NodeType, Set[str]] = field(default_factory=dict)

    def re_refs(self, type: NodeType):
        if type in self.REF_KINDS:
            return self._redefine_references.setdefault(type, {})
        else:
            raise KeyError(f"Unsupported ref type ({type}) for container. ")

    def del_refs(self, type: NodeType):
        if type in self.REF_KINDS:
            return self._remove_references.setdefault(type, set())
        else:
            raise KeyError(f"Unsupported ref type ({type}) for container. ")


    # something

    # Implement
    # def refs(self, type: NodeType):
    # create output container
    # add parent references
    # redefine
    # remove
    # return container
