from copy import deepcopy
from pathlib import Path
from textwrap import dedent

from pycps_sysmlv2 import NodeType
from pycps_sysmlv2.definitions import SysMLType
from pycps_sysmlv2.definitions.base import InherenceDefinition


def write_model(path: Path, content: str) -> None:
    path.write_text(content.strip() + "\n")


def write_package(path: Path, body: str, package_name: str = "Example") -> None:
    normalized_body = dedent(body).strip()
    write_model(
        path,
        f"""
        package {package_name} {{
        {normalized_body}
        }}
        """,
    )


def _format_type(value) -> str:
    if isinstance(value, SysMLType):
        return value.as_string()
    return str(value)


def _format_value(value) -> str:
    return repr(value)


def _format_doc(node) -> str:
    return f' doc="{node.doc}"' if node.doc else ""


def _format_def_header(prefix: str, definition) -> str:
    specializes = ""
    if isinstance(definition, InherenceDefinition) and definition.specializes:
        specializes = f" specializes {definition.specializes}"
    return f"{prefix} {definition.name}{specializes}{_format_doc(definition)}"


def architecture_structure(architecture) -> str:
    architecture = deepcopy(architecture)
    lines = [f"package {architecture.package}"]

    for name in sorted(architecture.part_definitions):
        part = architecture.part_definitions[name]
        lines.append(_format_def_header("part", part))

        attrs = part.defs(NodeType.Attribute)
        for key in sorted(attrs):
            attr = attrs[key]
            lines.append(
                f"  attr {attr.name}:{_format_type(attr.type)}={_format_value(attr.value)}{_format_doc(attr)}"
            )

        parts = part.refs(NodeType.Part)
        for key in sorted(parts):
            ref = parts[key]
            target = ref.ref_node.name if ref.ref_node is not None else "?"
            lines.append(f"  part {ref.name}:{ref.type} -> {target}{_format_doc(ref)}")

        ports = part.refs(NodeType.Port)
        for key in sorted(ports):
            ref = ports[key]
            target = ref.ref_node.name if ref.ref_node is not None else "?"
            lines.append(
                f"  port {ref.direction} {ref.name}:{ref.type} -> {target}{_format_doc(ref)}"
            )

        reqs = part.refs(NodeType.Requirement)
        for key in sorted(reqs):
            ref = reqs[key]
            target = ref.ref_node.name if ref.ref_node is not None else "?"
            lines.append(f"  req {ref.name}:{ref.type} -> {target}{_format_doc(ref)}")

        connections = part.defs(NodeType.Connection)
        for key in sorted(connections):
            conn = connections[key]
            lines.append(
                f"  connect {conn.src_part}.{conn.src_port} -> {conn.dst_part}.{conn.dst_port}"
            )

    for name in sorted(architecture.port_definitions):
        port = architecture.port_definitions[name]
        lines.append(_format_def_header("port", port))

        attrs = port.defs(NodeType.Attribute)
        for key in sorted(attrs):
            attr = attrs[key]
            lines.append(
                f"  attr {attr.name}:{_format_type(attr.type)}={_format_value(attr.value)}{_format_doc(attr)}"
            )

        reqs = port.refs(NodeType.Requirement)
        for key in sorted(reqs):
            ref = reqs[key]
            target = ref.ref_node.name if ref.ref_node is not None else "?"
            lines.append(f"  req {ref.name}:{ref.type} -> {target}{_format_doc(ref)}")

    for name in sorted(architecture.requirement_definitions):
        req = architecture.requirement_definitions[name]
        lines.append(_format_def_header("requirement", req))

        attrs = req.defs(NodeType.Attribute)
        for key in sorted(attrs):
            attr = attrs[key]
            lines.append(
                f"  attr {attr.name}:{_format_type(attr.type)}={_format_value(attr.value)}{_format_doc(attr)}"
            )

    return "\n".join(lines) + "\n"


def assert_architecture_structure(architecture, expected: str) -> None:
    expected_norm = dedent(expected).strip() + "\n"
    assert architecture_structure(architecture) == expected_norm
