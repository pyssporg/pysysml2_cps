"""Traceability Preamble
Template ID: PYCSYSML2_TRACE_PREAMBLE
Template Version: 1.1.0
Purpose: Connection model definitions linking parts and ports.
Design Notes:
- Capture connection endpoints in explicit references for traceable linking.
- Support serialization/export of both declared and inherited connections.
Key Invariants:
- Connection endpoint references must remain resolvable within package context.
- Connection naming and directionality text must remain parser/export compatible.
Strongly Connected External Modules:
- pycps_sysmlv2.definitions.references
Decision Log:
- Add dated, behavior-impacting decisions; avoid logging template-only edits.
"""
from __future__ import annotations

from dataclasses import dataclass
from .base import SysMLBase, DefinitionBase, NodeType


@dataclass(kw_only=True)
class SysMLConnection(SysMLBase):
    src_part: str
    src_port: str
    dst_part: str
    dst_port: str

    src_part_node: "SysMLPartDefinition" = None
    dst_part_node: "SysMLPartDefinition" = None
    src_port_node: "SysMLPortDefinition" = None
    dst_port_node: "SysMLPortDefinition" = None

    @property
    def key(self):
        return self.get_connection_key(
            self.src_part,
            self.src_port,
            self.dst_part,
            self.dst_port,
        )

    @staticmethod
    def get_connection_key(
        src_part: str, src_port: str, dst_part: str, dst_port: str
    ) -> str:
        return f"{src_part}.{src_port}->{dst_part}.{dst_port}"

    @staticmethod
    def from_names(
        namespace: DefinitionBase,
        src_part: str,
        src_port: str,
        dst_part: str,
        dst_port: str,
    ):
        src_part_node = namespace.get_def(NodeType.Part, src_part)
        dst_part_node = namespace.get_def(NodeType.Part, dst_part)
        src_port_node = namespace.get_def(NodeType.Port, src_port)
        dst_port_node = namespace.get_def(NodeType.Port, dst_port)
        return SysMLConnection(
            src_part=src_part,
            src_port=src_port,
            dst_part=dst_part,
            dst_port=dst_port,
            src_part_node=src_part_node,
            src_port_node=src_port_node,
            dst_part_node=dst_part_node,
            dst_port_node=dst_port_node,
        )
