"""Data model definitions for lightweight SysML parsing."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from .parser_utils import json_dumps
from .utils import obj_base

import ast
#  Definitions


class PrimitiveType(str, Enum):
    Boolean = "Boolean"
    Integer = "Integer"
    Real = "Real"
    String = "String"
    Null = "Null"
    Unknown = "Unknown"


SYSML_TYPE_MAP = {
    "real": PrimitiveType.Real,
    "float": PrimitiveType.Real,
    "float32": PrimitiveType.Real,
    "float64": PrimitiveType.Real,
    "double": PrimitiveType.Real,
    "integer": PrimitiveType.Integer,
    "int": PrimitiveType.Integer,
    "int8": PrimitiveType.Integer,
    "int32": PrimitiveType.Integer,
    "uint8": PrimitiveType.Integer,
    "uint32": PrimitiveType.Integer,
    "boolean": PrimitiveType.Boolean,
    "bool": PrimitiveType.Boolean,
    "string": PrimitiveType.String,
}


class SysMLType:
    def __init__(self, type: PrimitiveType, string_definition: Optional[str] = None):
        self.type = type
        self.string_definition = string_definition

    def is_unknown(self):
        return self.type == PrimitiveType.Unknown

    def primitive_type(self):
        return obj_base(self.type)

    def primitive_type_str(self):
        return self._as_string(obj_base(self.type))

    def as_string(self):
        return self._as_string(self.type)

    # Static methods

    @staticmethod
    def _as_string(type):
        if isinstance(type, (list, tuple)):
            if len(type) == 0:
                return "List[]"
            else:
                return f"List[{SysMLType._as_string(type[0])}]"
        if isinstance(type, Enum):
            return str(type.value)
        return str(type)

    @staticmethod
    def from_value(value):
        return SysMLType(SysMLType._from_value(value))

    @staticmethod
    def _from_value(value):
        if value is None:
            return PrimitiveType.Null
        if isinstance(value, bool):
            return PrimitiveType.Boolean
        if isinstance(value, int):
            return PrimitiveType.Integer
        if isinstance(value, float):
            return PrimitiveType.Real
        if isinstance(value, str):
            return PrimitiveType.String
        if isinstance(value, (list, tuple)):
            if len(value) == 0:
                return list()
            else:
                return [SysMLType._from_value(value[0])]

    @staticmethod
    def from_string(string: str) -> "SysMLType":
        # List types are not supported
        striped = string.strip().lower()
        if striped in SYSML_TYPE_MAP:
            return SysMLType(SYSML_TYPE_MAP[striped])
        return SysMLType(PrimitiveType.Unknown, string)

    def __str__(self) -> str:
        return json_dumps(self)


class SysMLAttribute:
    def __init__(
        self,
        name: str,
        type: Optional[SysMLType],
        value: Optional[Any],
        doc: Optional[str],
    ):
        self.name = name
        self.type = type
        self.value = value
        self.doc = doc

    def is_list(self):
        return isinstance(self.value, (list, tuple))

    def enumerator(self, start=0):
        v = self.value
        if not self.is_list():
            v = [v]
        return enumerate(v, start=start)

    @staticmethod
    def from_literal(name, value: Optional[str], doc: Optional[str]):
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
        else:
            return item

    def __str__(self) -> str:
        return json_dumps(self)


@dataclass
class SysMLRequirement:
    identifier: str
    text: str
    source_file: Optional[str] = None

    def __str__(self) -> str:
        return json_dumps(self)


@dataclass
class SysMLConnection:
    src_component: str
    src_port: str
    dst_component: str
    dst_port: str
    src_part_def: Optional["SysMLPartDefinition"] = None
    dst_part_def: Optional["SysMLPartDefinition"] = None
    src_port_def: Optional["SysMLPortDefinition"] = None
    dst_port_def: Optional["SysMLPortDefinition"] = None

    def __str__(self) -> str:
        return json_dumps(self)


@dataclass
class SysMLPortDefinition:
    name: str
    doc: Optional[str] = None
    attributes: Dict[str, SysMLAttribute] = field(default_factory=dict)
    source_file: Optional[str] = None

    def __str__(self) -> str:
        return json_dumps(self)


@dataclass
class SysMLPartDefinition:
    name: str
    doc: Optional[str] = None
    base_part_name: Optional[str] = None
    base_part_def: Optional["SysMLPartDefinition"] = None
    source_file: Optional[str] = None
    attributes: Dict[str, SysMLAttribute] = field(default_factory=dict)
    ports: Dict[str, SysMLPortReference] = field(default_factory=dict)
    parts: Dict[str, SysMLPartReference] = field(default_factory=dict)
    connections: List[SysMLConnection] = field(default_factory=list)
    declared_attributes: Dict[str, SysMLAttribute] = field(default_factory=dict)
    declared_ports: Dict[str, SysMLPortReference] = field(default_factory=dict)
    declared_parts: Dict[str, SysMLPartReference] = field(default_factory=dict)
    declared_connections: List[SysMLConnection] = field(default_factory=list)
    replace_attributes: Dict[str, SysMLAttribute] = field(default_factory=dict)
    replace_ports: Dict[str, SysMLPortReference] = field(default_factory=dict)
    replace_parts: Dict[str, SysMLPartReference] = field(default_factory=dict)
    remove_attributes: Set[str] = field(default_factory=set)
    remove_ports: Set[str] = field(default_factory=set)
    remove_parts: Set[str] = field(default_factory=set)
    remove_connections: List[SysMLConnection] = field(default_factory=list)

    def get_port_attributes(
        self,
    ) -> List[Tuple[SysMLPortReference, SysMLPortDefinition, SysMLAttribute]]:
        attributes = []
        for port in self.ports.values():
            port_def = port.port_def
            if port_def is None:
                raise ValueError(
                    f"Port definition not resolved for {self.name}.{port.name} ({port.port_name})"
                )
            for attr in port_def.attributes.values():
                s = (port, port_def, attr)
                attributes.append(s)
        return attributes

    def __str__(self) -> str:
        return json_dumps(self)


#  References


@dataclass
class SysMLPartReference:
    name: str
    part_name: str
    doc: Optional[str] = None
    part_def: Optional["SysMLPartDefinition"] = None

    def __str__(self) -> str:
        return json_dumps(self)


@dataclass
class SysMLPortReference:
    name: str
    direction: str  # "in" or "out"
    port_name: str
    doc: Optional[str] = None
    port_def: Optional[SysMLPortDefinition] = None

    def __str__(self) -> str:
        return json_dumps(self)


#  Architecture


@dataclass
class SysMLArchitecture:
    package: str
    # keep port definitions before part definitions to ensure correct json export order
    port_definitions: Dict[str, SysMLPortDefinition] = field(default_factory=dict)
    part_definitions: Dict[str, SysMLPartDefinition] = field(default_factory=dict)
    requirements: List[SysMLRequirement] = field(default_factory=list)

    def __str__(self) -> str:
        return json_dumps(self)

    def __post_init__(self):

        # To ensure json export order
        self.part_definitions = dict(
            sorted(
                self.part_definitions.items(),
                key=lambda item: (len(item[1].parts), item[0]),
                reverse=False,
            )
        )
