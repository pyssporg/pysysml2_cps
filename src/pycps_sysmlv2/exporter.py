"""SysML text export helpers."""

from __future__ import annotations

from typing import Dict, Iterable, List

from .definitions import (
    SysMLArchitecture,
    SysMLAttribute,
    SysMLPartDefinition,
    SysMLPartReference,
    SysMLPortReference,
)


class SysMLExporter:
    def __init__(self, indent: str = "  "):
        self.indent = indent

    def export_architecture(self, architecture: SysMLArchitecture, mode: str = "declared") -> str:
        lines = [f"package {architecture.package} {{"]
        lines.extend(self._emit_port_definitions(architecture, level=1))
        if architecture.port_definitions:
            lines.append("")
        lines.extend(self._emit_part_definitions(architecture, level=1, mode=mode))
        lines.append("}")
        return "\n".join(line for line in lines if line is not None) + "\n"

    def export_architecture_files(
        self, architecture: SysMLArchitecture, mode: str = "declared"
    ) -> Dict[str, str]:
        if mode == "flattened":
            return {"architecture.sysml": self.export_architecture(architecture, mode=mode)}

        grouped_parts: Dict[str, Dict[str, SysMLPartDefinition]] = {}
        for name, part in architecture.part_definitions.items():
            file_name = part.source_file or "architecture.sysml"
            grouped_parts.setdefault(file_name, {})[name] = part

        file_texts: Dict[str, str] = {}
        for file_name, file_parts in sorted(grouped_parts.items()):
            lines = [f"package {architecture.package} {{"]
            # Include all port definitions so file exports remain self-contained.
            lines.extend(self._emit_port_definitions(architecture, level=1))
            if architecture.port_definitions and file_parts:
                lines.append("")
            lines.extend(self._emit_part_definitions_subset(file_parts, level=1, mode=mode))
            lines.append("}")
            file_texts[file_name] = "\n".join(lines) + "\n"
        return file_texts

    def _emit_port_definitions(self, architecture: SysMLArchitecture, level: int) -> List[str]:
        lines: List[str] = []
        pad = self.indent * level
        for name in sorted(architecture.port_definitions):
            port = architecture.port_definitions[name]
            lines.append(f"{pad}port def {port.name} {{")
            attrs = port.items.get("attributes", port.attributes)
            for attr in sorted(attrs.values(), key=lambda a: a.name):
                lines.append(f"{pad}{self.indent}{self._format_attribute(attr)}")
            lines.append(f"{pad}}}")
            lines.append("")
        if lines and lines[-1] == "":
            lines.pop()
        return lines

    def _emit_part_definitions(
        self, architecture: SysMLArchitecture, level: int, mode: str
    ) -> List[str]:
        return self._emit_part_definitions_subset(architecture.part_definitions, level, mode)

    def _emit_part_definitions_subset(
        self, part_definitions: Dict[str, SysMLPartDefinition], level: int, mode: str
    ) -> List[str]:
        lines: List[str] = []
        pad = self.indent * level
        for name in sorted(part_definitions):
            part = part_definitions[name]
            if mode == "flattened":
                header = f"{pad}part def {part.name} {{"
            else:
                header = f"{pad}part def {part.name}"
                if part.base_part_name is not None:
                    header += f" specializes {part.base_part_name}"
                header += " {"
            lines.append(header)
            if mode == "flattened":
                lines.extend(self._emit_flattened_members(part, level + 1))
            else:
                lines.extend(self._emit_declared_members(part, level + 1))
            lines.append(f"{pad}}}")
            lines.append("")
        if lines and lines[-1] == "":
            lines.pop()
        return lines

    def _emit_declared_members(self, part: SysMLPartDefinition, level: int) -> List[str]:
        pad = self.indent * level
        lines: List[str] = []
        for kind in ("attributes", "ports", "parts"):
            singular = kind[:-1]
            for name in sorted(part.remove_items.get(kind, set())):
                lines.append(f"{pad}remove {singular} {name};")
        for connection in part.remove_connections:
            lines.append(f"{pad}{self._format_remove_connection(connection)}")

        for kind in ("attributes", "ports", "parts"):
            values = part.redefines_items.get(kind, {})
            for name in sorted(values):
                lines.append(f"{pad}redefines {self._format_member(kind, values[name])}")

        for kind in ("attributes", "ports", "parts"):
            values = part.items.get(kind, {})
            for name in sorted(values):
                lines.append(f"{pad}{self._format_member(kind, values[name])}")
        for connection in part.declared_connections:
            lines.append(f"{pad}{self._format_connection(connection)}")
        return lines

    def _emit_flattened_members(self, part: SysMLPartDefinition, level: int) -> List[str]:
        pad = self.indent * level
        lines: List[str] = []
        for attr in sorted(part.attributes.values(), key=lambda a: a.name):
            lines.append(f"{pad}{self._format_attribute(attr)}")
        for port in sorted(part.ports.values(), key=lambda p: p.name):
            lines.append(f"{pad}{self._format_port_ref(port)}")
        for subpart in sorted(part.parts.values(), key=lambda p: p.name):
            lines.append(f"{pad}{self._format_part_ref(subpart)}")
        for connection in part.connections:
            lines.append(f"{pad}{self._format_connection(connection)}")
        return lines

    def _format_attribute(self, attr: SysMLAttribute) -> str:
        if attr.value is not None:
            return f"attribute {attr.name} = {self._format_value(attr.value)};"
        if attr.type is not None:
            return f"attribute {attr.name} : {attr.type.as_string()};"
        return f"attribute {attr.name};"

    def _format_port_ref(self, port: SysMLPortReference) -> str:
        return f"{port.direction} port {port.name} : {port.port_name};"

    def _format_part_ref(self, part: SysMLPartReference) -> str:
        return f"part {part.name} : {part.part_name};"

    def _format_member(self, kind: str, value: object) -> str:
        if kind == "attributes":
            return self._format_attribute(value)  # type: ignore[arg-type]
        if kind == "ports":
            return self._format_port_ref(value)  # type: ignore[arg-type]
        if kind == "parts":
            return self._format_part_ref(value)  # type: ignore[arg-type]
        raise ValueError(f"Unsupported member kind for export: {kind}")

    def _format_connection(self, connection) -> str:
        return (
            f"connect {connection.src_component}.{connection.src_port} "
            f"to {connection.dst_component}.{connection.dst_port};"
        )

    def _format_remove_connection(self, connection) -> str:
        return (
            f"remove connect {connection.src_component}.{connection.src_port} "
            f"to {connection.dst_component}.{connection.dst_port};"
        )

    def _format_value(self, value: object) -> str:
        if isinstance(value, str):
            return f"\"{value}\""
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, list):
            return "[" + ", ".join(self._format_value(v) for v in value) + "]"
        return repr(value)


def export_architecture(architecture: SysMLArchitecture, mode: str = "declared") -> str:
    return SysMLExporter().export_architecture(architecture, mode=mode)


def export_architecture_files(
    architecture: SysMLArchitecture, mode: str = "declared"
) -> Dict[str, str]:
    return SysMLExporter().export_architecture_files(architecture, mode=mode)
