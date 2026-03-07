from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from ..utils import obj_base
from .base import SysMLBase


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

@dataclass(kw_only=True)
class SysMLType(SysMLBase):
    type : PrimitiveType
    string_definition : Optional[str] = None

    def is_unknown(self):
        return self.type == PrimitiveType.Unknown

    def primitive_type(self):
        return obj_base(self.type)

    def primitive_type_str(self):
        return self._as_string(obj_base(self.type))

    def as_string(self):
        return self._as_string(self.type)

    @staticmethod
    def _as_string(type):
        if isinstance(type, (list, tuple)):
            if len(type) == 0:
                return "List[]"
            return f"List[{SysMLType._as_string(type[0])}]"
        if isinstance(type, Enum):
            return str(type.value)
        return str(type)

    @staticmethod
    def from_value(value):
        return SysMLType(type=SysMLType._from_value(value))

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
            return [SysMLType._from_value(value[0])]

    @staticmethod
    def from_string(string: str) -> "SysMLType":
        striped = string.strip().lower()
        if striped in SYSML_TYPE_MAP:
            return SysMLType(type=SYSML_TYPE_MAP[striped])
        return SysMLType(type=PrimitiveType.Unknown, string_definition=string)
