"""SysML text export helpers."""

from __future__ import annotations

from typing import Dict, List

from .definitions import (
    SysMLArchitecture,
    SysMLAttribute,
    SysMLPartDefinition,
    SysMLPartReference,
    SysMLPortReference,
    SysMLRequirementDefinition,
    SysMLRequirementReference,
)


class SysMLExporter:
    def __init__(self, indent: str = "  "):
        self.indent = indent

    def export_flattened(self, architecture: SysMLArchitecture) -> str:
        lines = [f"package {architecture.package} {{"]
        lines.extend(
            self._emit_requirement_definitions_subset(
                architecture.requirement_definitions,
                level=1,
            )
        )
        if architecture.requirement_definitions:
            lines.append("")
        lines.extend(
            self._emit_port_definitions_subset(
                architecture.port_definitions,
                level=1,
                mode="flattened",
            )
        )
        if architecture.port_definitions:
            lines.append("")
        lines.extend(
            self._emit_part_definitions_subset(
                architecture.part_definitions,
                level=1,
                mode="flattened",
            )
        )
        lines.append("}")
        return "\n".join(line for line in lines if line is not None) + "\n"

    def export_declared(self, architecture: SysMLArchitecture) -> Dict[str, str]:
        grouped_requirements: Dict[str, Dict[str, SysMLRequirementDefinition]] = {}
        grouped_parts: Dict[str, Dict[str, SysMLPartDefinition]] = {}
        grouped_ports: Dict[str, Dict[str, object]] = {}

        for name, requirement in architecture.requirement_definitions.items():
            file_name = requirement.source_file or "architecture.sysml"
            grouped_requirements.setdefault(file_name, {})[name] = requirement
        for name, part in architecture.part_definitions.items():
            file_name = part.source_file or "architecture.sysml"
            grouped_parts.setdefault(file_name, {})[name] = part
        for name, port in architecture.port_definitions.items():
            file_name = port.source_file or "architecture.sysml"
            grouped_ports.setdefault(file_name, {})[name] = port

        file_texts: Dict[str, str] = {}
        file_names = sorted(set(grouped_requirements) | set(grouped_parts) | set(grouped_ports))
        for file_name in file_names:
            file_requirements = grouped_requirements.get(file_name, {})
            file_parts = grouped_parts.get(file_name, {})
            file_ports = grouped_ports.get(file_name, {})

            lines = [f"package {architecture.package} {{"]
            lines.extend(self._emit_requirement_definitions_subset(file_requirements, level=1))
            if file_requirements and (file_ports or file_parts):
                lines.append("")
            lines.extend(
                self._emit_port_definitions_subset(
                    file_ports,
                    level=1,
                    mode="declared",
                )
            )
            if file_ports and file_parts:
                lines.append("")
            lines.extend(
                self._emit_part_definitions_subset(
                    file_parts,
                    level=1,
                    mode="declared",
                )
            )
            lines.append("}")
            file_texts[file_name] = "\n".join(lines) + "\n"
        return file_texts

    def _emit_requirement_definitions_subset(
        self, requirement_definitions: Dict[str, SysMLRequirementDefinition], level: int
    ) -> List[str]:
        lines: List[str] = []
        pad = self.indent * level
        for name in sorted(requirement_definitions):
            requirement = requirement_definitions[name]
            header = f"{pad}requirement def {requirement.name}"
            if requirement.specializes is not None:
                header += f" specializes {requirement.specializes}"
            header += " {"
            lines.append(header)
            if requirement.text:
                lines.append(f"{pad}{self.indent}doc /* {requirement.text} */")
            lines.append(f"{pad}}}")
            lines.append("")
        if lines and lines[-1] == "":
            lines.pop()
        return lines

    def _emit_port_definitions_subset(
        self, port_definitions: Dict[str, object], level: int, mode: str
    ) -> List[str]:
        lines: List[str] = []
        pad = self.indent * level
        for name in sorted(port_definitions):
            port = port_definitions[name]
            header = f"{pad}port def {port.name}"
            if mode != "flattened" and port.specializes is not None:
                header += f" specializes {port.specializes}"
            header += " {"
            lines.append(header)
            attrs = port.items.get("attributes", {})
            for attr in sorted(attrs.values(), key=lambda a: a.name):
                lines.append(f"{pad}{self.indent}{self._format_attribute(attr)}")
            reqs = port.items.get("requirements", {})
            for req_name in sorted(reqs):
                lines.append(f"{pad}{self.indent}{self._format_requirement_ref(reqs[req_name])}")
            lines.append(f"{pad}}}")
            lines.append("")
        if lines and lines[-1] == "":
            lines.pop()
        return lines

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
                base_name = part.specializes
                if base_name is not None:
                    header += f" specializes {base_name}"
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
        declared_items = getattr(part, "declared_items", part.items)
        for kind in ("attributes", "ports", "parts", "requirements"):
            singular = kind[:-1]
            for name in sorted(part.remove_items.get(kind, set())):
                lines.append(f"{pad}remove {singular} {name};")
        for key in sorted(part.remove_items.get("connections", set())):
            lines.append(f"{pad}{self._format_remove_connection_key(key)}")

        for kind in ("attributes", "ports", "parts", "requirements"):
            values = part.redefines_items.get(kind, {})
            for name in sorted(values):
                lines.append(f"{pad}redefines {self._format_member(kind, values[name])}")

        for kind in ("attributes", "ports", "parts", "requirements"):
            values = declared_items.get(kind, {})
            for name in sorted(values):
                lines.append(f"{pad}{self._format_member(kind, values[name])}")
        for connection in declared_items.get("connections", {}).values():
            lines.append(f"{pad}{self._format_connection(connection)}")
        return lines

    def _emit_flattened_members(self, part: SysMLPartDefinition, level: int) -> List[str]:
        pad = self.indent * level
        lines: List[str] = []
        for attr in sorted(part.items.get("attributes", {}).values(), key=lambda a: a.name):
            lines.append(f"{pad}{self._format_attribute(attr)}")
        for port in sorted(part.items.get("ports", {}).values(), key=lambda p: p.name):
            lines.append(f"{pad}{self._format_port_ref(port)}")
        for subpart in sorted(part.items.get("parts", {}).values(), key=lambda p: p.name):
            lines.append(f"{pad}{self._format_part_ref(subpart)}")
        for requirement in sorted(
            part.items.get("requirements", {}).values(), key=lambda r: r.name
        ):
            lines.append(f"{pad}{self._format_requirement_ref(requirement)}")
        for connection in part.items.get("connections", {}).values():
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
        if kind == "requirements":
            return self._format_requirement_ref(value)  # type: ignore[arg-type]
        raise ValueError(f"Unsupported member kind for export: {kind}")

    def _format_requirement_ref(self, requirement: SysMLRequirementReference) -> str:
        if requirement.requirement_name == requirement.name:
            return f"requirement {requirement.name};"
        return f"requirement {requirement.name} : {requirement.requirement_name};"

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

    def _format_remove_connection_key(self, key: str) -> str:
        src, dst = key.split("->", 1)
        src_component, src_port = src.split(".", 1)
        dst_component, dst_port = dst.split(".", 1)
        return (
            f"remove connect {src_component}.{src_port} "
            f"to {dst_component}.{dst_port};"
        )

    def _format_value(self, value: object) -> str:
        if isinstance(value, str):
            return f'"{value}"'
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, list):
            return "[" + ", ".join(self._format_value(v) for v in value) + "]"
        return repr(value)

