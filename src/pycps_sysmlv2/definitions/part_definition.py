"""Traceability Preamble
Template ID: PYCSYSML2_TRACE_PREAMBLE
Template Version: 1.1.0
Purpose: Part definition model and helpers for owned members.
Design Notes:
- Model parts with nested ports/attributes/connections for rich architecture graphs.
- Keep ownership semantics explicit via parent relationships.
Key Invariants:
- Part member collections must preserve deterministic iteration order.
- Specialization references should remain explicit strings until resolution.
Strongly Connected External Modules:
- pycps_sysmlv2.definitions.attributes
- pycps_sysmlv2.definitions.connections
Decision Log:
- Add dated, behavior-impacting decisions; avoid logging template-only edits.
"""
from __future__ import annotations

from dataclasses import dataclass

from .base import InherenceDefinition, NodeType


@dataclass
class SysMLPartDefinition(InherenceDefinition):
    DEF_KINDS: tuple[NodeType, ...] = (
        NodeType.Attribute,
        NodeType.Part,
        NodeType.Port,
        NodeType.Requirement,
        NodeType.Connection,
    )
    REF_KINDS: tuple[NodeType, ...] = (
        NodeType.Part,
        NodeType.Port,
        NodeType.Requirement,
    )

    def export_dot(self, graph_name: str | None = None) -> str:
        """Export contained part references and grouped part-to-part links as Graphviz DOT."""
        part_names = set(self.refs(NodeType.Part))
        grouped_edges: set[tuple[str, str]] = set()

        for connection in self.defs(NodeType.Connection).values():
            part_names.add(connection.src_part)
            part_names.add(connection.dst_part)
            grouped_edges.add((connection.src_part, connection.dst_part))

        dot_graph_name = self._dot_quote(graph_name or self.name or "SysMLPartDefinition")
        lines = [f"digraph {dot_graph_name} {{"]

        for part_name in sorted(part_names):
            quoted_name = self._dot_quote(part_name)
            lines.append(f"  {quoted_name};")

        for src_part, dst_part in sorted(grouped_edges):
            lines.append(f"  {self._dot_quote(src_part)} -> {self._dot_quote(dst_part)};")

        lines.append("}")
        return "\n".join(lines) + "\n"

    @staticmethod
    def _dot_quote(value: str) -> str:
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'

