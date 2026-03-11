"""SysML text export helpers."""

from __future__ import annotations

from typing import Dict, List

from .definitions import (
    SysMLPackage,
    SysMLAttribute,
    SysMLPartDefinition,
    SysMLPortDefinition,
    SysMLPartReference,
    SysMLPortReference,
    SysMLRequirementDefinition,
    SysMLRequirementReference,
    SysMLConnection,
    NodeType,
)


class SysMLExporter:
    def __init__(self, indent: str = "  "):
        self.indent = indent

    def export_flattened(self, architecture: SysMLPackage) -> str:
        lines = [f"package {architecture.package} {{"]
        requirement_definitions = architecture.defs(NodeType.Requirement)
        port_definitions = architecture.defs(NodeType.Port)
        part_definitions = architecture.defs(NodeType.Part)
        lines.extend(
            self._emit_requirement_definitions_subset(
                requirement_definitions,
                level=1,
            )
        )
        if requirement_definitions:
            lines.append("")
        lines.extend(
            self._emit_port_definitions_subset(
                port_definitions,
                level=1,
                mode="flattened",
            )
        )
        if port_definitions:
            lines.append("")
        lines.extend(
            self._emit_part_definitions_subset(
                part_definitions,
                level=1,
                mode="flattened",
            )
        )
        lines.append("}")
        return "\n".join(line for line in lines if line is not None) + "\n"

    def export_declared(self, architecture: SysMLPackage) -> Dict[str, str]:
        grouped_requirements: Dict[str, Dict[str, SysMLRequirementDefinition]] = {}
        grouped_parts: Dict[str, Dict[str, SysMLPartDefinition]] = {}
        grouped_ports: Dict[str, Dict[str, object]] = {}

        requirement_definitions = architecture.defs(NodeType.Requirement)
        part_definitions = architecture.defs(NodeType.Part)
        port_definitions = architecture.defs(NodeType.Port)

        for name, requirement in requirement_definitions.items():
            file_name = requirement.source_file or "architecture.sysml"
            grouped_requirements.setdefault(file_name, {})[name] = requirement
        for name, part in part_definitions.items():
            file_name = part.source_file or "architecture.sysml"
            grouped_parts.setdefault(file_name, {})[name] = part
        for name, port in port_definitions.items():
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
            base_name = self._specializes_name(requirement)
            if base_name is not None:
                header += f" specializes {base_name}"
            header += " {"
            lines.append(header)
            req_text = self._requirement_text(requirement)
            if req_text:
                lines.append(f"{pad}{self.indent}doc /* {req_text} */")
            lines.append(f"{pad}}}")
            lines.append("")
        if lines and lines[-1] == "":
            lines.pop()
        return lines

    def _emit_port_definitions_subset(
        self, port_definitions: Dict[str, SysMLPortDefinition], level: int, mode: str
    ) -> List[str]:
        lines: List[str] = []
        pad = self.indent * level
        for name in sorted(port_definitions):
            port = port_definitions[name]
            header = f"{pad}port def {port.name}"
            base_name = self._specializes_name(port)
            if mode != "flattened" and base_name is not None:
                header += f" specializes {base_name}"
            header += " {"
            lines.append(header)
            if mode == "flattened":
                attrs = port.defs(NodeType.Attribute)
                for attr in sorted(attrs.values(), key=lambda a: a.name):
                    lines.append(f"{pad}{self.indent}{self._format_attribute(attr)}")
                reqs = port.refs(NodeType.Requirement)
                for req_name in sorted(reqs):
                    lines.append(
                        f"{pad}{self.indent}{self._format_requirement_ref(reqs[req_name])}"
                    )
            else:
                lines.extend(self._emit_declared_port_members(port, level + 1))
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
                base_name = self._specializes_name(part)
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
        declared_defs = {kind: dict(part._defs.get(kind, {})) for kind in part.DEF_KINDS}
        declared_refs = {kind: dict(part._refs.get(kind, {})) for kind in part.REF_KINDS}

        for kind in (NodeType.Attribute, NodeType.Port, NodeType.Part, NodeType.Requirement):
            singular = self._kind_singular(kind)
            remove_values = (
                part.remove_refs(kind) if kind in part.REF_KINDS else part.remove_defs(kind)
            )
            for name in sorted(remove_values):
                lines.append(f"{pad}remove {singular} {name};")
        for key in sorted(part.remove_defs(NodeType.Connection)):
            lines.append(f"{pad}{self._format_remove_connection_key(key)}")

        for kind in (NodeType.Attribute, NodeType.Port, NodeType.Part, NodeType.Requirement):
            values = (
                part.redefine_refs(kind)
                if kind in part.REF_KINDS
                else part.redefine_defs(kind)
            )
            for name in sorted(values):
                lines.append(f"{pad}redefines {self._format_member(kind, values[name])}")

        for kind, values in (
            (NodeType.Attribute, declared_defs.get(NodeType.Attribute, {})),
            (NodeType.Port, declared_refs.get(NodeType.Port, {})),
            (NodeType.Part, declared_refs.get(NodeType.Part, {})),
            (NodeType.Requirement, declared_refs.get(NodeType.Requirement, {})),
        ):
            for name in sorted(values):
                lines.append(f"{pad}{self._format_member(kind, values[name])}")
        for connection in declared_defs.get(NodeType.Connection, {}).values():
            lines.append(f"{pad}{self._format_connection(connection)}")
        return lines

    def _emit_declared_port_members(self, port: SysMLPortDefinition, level: int) -> List[str]:
        pad = self.indent * level
        lines: List[str] = []

        for name in sorted(port.remove_defs(NodeType.Attribute)):
            lines.append(f"{pad}remove attribute {name};")
        for name in sorted(port.remove_refs(NodeType.Requirement)):
            lines.append(f"{pad}remove requirement {name};")

        for name in sorted(port.redefine_defs(NodeType.Attribute)):
            lines.append(
                f"{pad}redefines {self._format_attribute(port.redefine_defs(NodeType.Attribute)[name])}"
            )
        for name in sorted(port.redefine_refs(NodeType.Requirement)):
            lines.append(
                f"{pad}redefines {self._format_requirement_ref(port.redefine_refs(NodeType.Requirement)[name])}"
            )

        for attr in sorted(port._defs.get(NodeType.Attribute, {}).values(), key=lambda a: a.name):
            lines.append(f"{pad}{self._format_attribute(attr)}")
        for req_name in sorted(port._refs.get(NodeType.Requirement, {})):
            lines.append(
                f"{pad}{self._format_requirement_ref(port._refs[NodeType.Requirement][req_name])}"
            )

        return lines

    def _emit_flattened_members(self, part: SysMLPartDefinition, level: int) -> List[str]:
        pad = self.indent * level
        lines: List[str] = []
        for attr in sorted(part.defs(NodeType.Attribute).values(), key=lambda a: a.name):
            lines.append(f"{pad}{self._format_attribute(attr)}")
        for port in sorted(part.refs(NodeType.Port).values(), key=lambda p: p.name):
            lines.append(f"{pad}{self._format_port_ref(port)}")
        for subpart in sorted(part.refs(NodeType.Part).values(), key=lambda p: p.name):
            lines.append(f"{pad}{self._format_part_ref(subpart)}")
        for requirement in sorted(
            part.refs(NodeType.Requirement).values(), key=lambda r: r.name
        ):
            lines.append(f"{pad}{self._format_requirement_ref(requirement)}")
        for connection in part.defs(NodeType.Connection).values():
            lines.append(f"{pad}{self._format_connection(connection)}")
        return lines

    def _format_attribute(self, attr: SysMLAttribute) -> str:
        if attr.value is not None:
            return f"attribute {attr.name} = {self._format_value(attr.value)};"
        if attr.type is not None:
            return f"attribute {attr.name} : {attr.type.as_string()};"
        return f"attribute {attr.name};"

    def _format_port_ref(self, port: SysMLPortReference) -> str:
        return f"{port.direction} port {port.name} : {port.type};"

    def _format_part_ref(self, part: SysMLPartReference) -> str:
        return f"part {part.name} : {part.type};"

    def _format_member(self, kind: NodeType, value: object) -> str:
        if kind == NodeType.Attribute:
            return self._format_attribute(value)  # type: ignore[arg-type]
        if kind == NodeType.Port:
            return self._format_port_ref(value)  # type: ignore[arg-type]
        if kind == NodeType.Part:
            return self._format_part_ref(value)  # type: ignore[arg-type]
        if kind == NodeType.Requirement:
            return self._format_requirement_ref(value)  # type: ignore[arg-type]
        raise ValueError(f"Unsupported member kind for export: {kind}")

    def _format_requirement_ref(self, requirement: SysMLRequirementReference) -> str:
        if requirement.type == requirement.name:
            return f"requirement {requirement.name};"
        return f"requirement {requirement.name} : {requirement.type};"

    def _format_connection(self, connection: SysMLConnection) -> str:
        return (
            f"connect {connection.src_part}.{connection.src_port} "
            f"to {connection.dst_part}.{connection.dst_port};"
        )

    def _format_remove_connection(self, connection: SysMLConnection) -> str:
        return (
            f"remove connect {connection.src_part}.{connection.src_port} "
            f"to {connection.dst_part}.{connection.dst_port};"
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

    def _specializes_name(self, definition: object) -> str | None:
        value = getattr(definition, "specializes", None)
        if value is None:
            return None
        return getattr(value, "name", value)

    def _kind_singular(self, kind: NodeType) -> str:
        return {
            NodeType.Attribute: "attribute",
            NodeType.Port: "port",
            NodeType.Part: "part",
            NodeType.Requirement: "requirement",
            NodeType.Connection: "connection",
        }.get(kind, str(kind))

    def _requirement_text(self, requirement: SysMLRequirementDefinition) -> str:
        try:
            return requirement.text
        except KeyError:
            return ""
