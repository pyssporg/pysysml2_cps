from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .base import DefinitionBase
from .part_definition import SysMLPartDefinition
from .port_definition import SysMLPortDefinition


@dataclass(kw_only=True)
class SysMLConnection(DefinitionBase):
    src_component: str
    src_port: str
    dst_component: str
    dst_port: str
    src_part_def: Optional[SysMLPartDefinition] = None
    dst_part_def: Optional[SysMLPartDefinition] = None
    src_port_def: Optional[SysMLPortDefinition] = None
    dst_port_def: Optional[SysMLPortDefinition] = None


    @property
    def key(self):
        return self.get_connection_key(self.src_component, self.src_port, self.dst_component, self.dst_port,)

    @staticmethod
    def get_connection_key(
        src_component: str, src_port: str, dst_component: str, dst_port: str
    ) -> str:
        return f"{src_component}.{src_port}->{dst_component}.{dst_port}"

