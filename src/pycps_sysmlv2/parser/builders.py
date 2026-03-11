"""Builders for SysML definitions parsed from blocks."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Dict, Optional

from ..definitions import (
    SysMLPartDefinition,
    SysMLPortDefinition,
    SysMLRequirementDefinition,
    NodeType,
    SysMLAttribute,
)
from ..parser_utils import strip_inline_comment
from .blocks import extract_requirement_blocks, iter_block_items
from .elements import (
    connection_key,
    parse_attribute,
    parse_connection,
    parse_part_reference,
    parse_port_endpoint,
    parse_removal,
    parse_replacement,
    parse_requirement_reference,
)
from .errors import unknown_statement_error


KIND_MAP = {
    "attributes": NodeType.Attribute,
    "parts": NodeType.Part,
    "ports": NodeType.Port,
    "requirements": NodeType.Requirement,
    "connections": NodeType.Connection,
}


def _map_kind(kind: str) -> NodeType:
    try:
        return KIND_MAP[kind]
    except KeyError as exc:
        raise ValueError(f"Unsupported member kind: {kind}") from exc


def _is_reference_kind(kind: NodeType) -> bool:
    return kind in (NodeType.Part, NodeType.Port, NodeType.Requirement)


def parse_part_block(
    name: str,
    block: str,
    base_part_name: Optional[str],
    source_path: Path,
    package_name: str,
    strict: bool,
) -> SysMLPartDefinition:
    part = SysMLPartDefinition(
        name=name,
        doc=None,
        specializes=base_part_name,
        source_file=source_path.name,
    )
    pending_doc: Optional[str] = None
    part_doc: Optional[str] = None

    for kind, payload in iter_block_items(block):
        if kind == "doc":
            has_members = any(part.defs(k) for k in part.DEF_KINDS) or any(
                part.refs(k) for k in part.REF_KINDS
            )
            if part_doc is None and not has_members:
                part_doc = payload
            else:
                pending_doc = payload
            continue

        line = strip_inline_comment(payload)
        if not line:
            continue

        if line.startswith("attribute "):
            attr = parse_attribute(line, pending_doc)
            part.add_def(NodeType.Attribute, attr.name, attr)
        elif line.startswith("in port "):
            port = parse_port_endpoint("in", line, pending_doc)
            part.add_ref(NodeType.Port, port.name, port)
        elif line.startswith("out port "):
            port = parse_port_endpoint("out", line, pending_doc)
            part.add_ref(NodeType.Port, port.name, port)
        elif line.startswith("part "):
            subpart = parse_part_reference(line, pending_doc)
            part.add_ref(NodeType.Part, subpart.name, subpart)
        elif line.startswith("requirement "):
            requirement = parse_requirement_reference(line, pending_doc)
            part.add_ref(NodeType.Requirement, requirement.name, requirement)
        elif line.startswith("connect "):
            connection = parse_connection(line)
            part.add_def(NodeType.Connection, connection_key(connection), connection)
        elif line.startswith("redefines "):
            replacement_kind, replacement_value = parse_replacement(
                line, pending_doc
            )
            mapped_kind = _map_kind(replacement_kind)
            if mapped_kind not in set(part.DEF_KINDS) | set(part.REF_KINDS):
                raise unknown_statement_error(
                    package_name=package_name,
                    source_path=source_path,
                    definition_kind="part def",
                    definition_name=name,
                    line=line,
                )
            if _is_reference_kind(mapped_kind):
                part.redefine_refs(mapped_kind)[replacement_value.name] = replacement_value
            else:
                part.redefine_defs(mapped_kind)[replacement_value.name] = replacement_value
        elif line.startswith("remove "):
            remove_kind, remove_key = parse_removal(line)
            mapped_kind = _map_kind(remove_kind)
            if mapped_kind not in set(part.DEF_KINDS) | set(part.REF_KINDS):
                raise unknown_statement_error(
                    package_name=package_name,
                    source_path=source_path,
                    definition_kind="part def",
                    definition_name=name,
                    line=line,
                )
            if _is_reference_kind(mapped_kind):
                part.remove_refs(mapped_kind).add(remove_key)
            else:
                part.remove_defs(mapped_kind).add(remove_key)
        elif strict:
            raise unknown_statement_error(
                package_name=package_name,
                source_path=source_path,
                definition_kind="part def",
                definition_name=name,
                line=line,
            )

        pending_doc = None

    part.doc = part_doc
    return part


def parse_port_block(
    name: str,
    block: str,
    base_port_name: Optional[str],
    source_path: Path,
    package_name: str,
    strict: bool,
) -> SysMLPortDefinition:
    port = SysMLPortDefinition(
        name=name,
        doc=None,
        specializes=base_port_name,
        source_file=source_path.name,
    )
    port_doc: Optional[str] = None
    pending_doc: Optional[str] = None

    for kind, payload in iter_block_items(block):
        if kind == "doc":
            has_members = any(port.defs(k) for k in port.DEF_KINDS) or any(
                port.refs(k) for k in port.REF_KINDS
            )
            if port_doc is None and not has_members:
                port_doc = payload
            else:
                pending_doc = payload
            continue

        line = strip_inline_comment(payload)
        if not line:
            continue

        if line.startswith("attribute "):
            attr = parse_attribute(line, pending_doc)
            port.add_def(NodeType.Attribute, attr.name, attr)
        elif line.startswith("requirement "):
            requirement = parse_requirement_reference(line, pending_doc)
            port.add_ref(NodeType.Requirement, requirement.name, requirement)
        elif line.startswith("redefines "):
            replacement_kind, replacement_value = parse_replacement(
                line, pending_doc
            )
            mapped_kind = _map_kind(replacement_kind)
            if mapped_kind not in set(port.DEF_KINDS) | set(port.REF_KINDS):
                raise unknown_statement_error(
                    package_name=package_name,
                    source_path=source_path,
                    definition_kind="port def",
                    definition_name=name,
                    line=line,
                )
            if _is_reference_kind(mapped_kind):
                port.redefine_refs(mapped_kind)[replacement_value.name] = replacement_value
            else:
                port.redefine_defs(mapped_kind)[replacement_value.name] = replacement_value
        elif line.startswith("remove "):
            remove_kind, remove_key = parse_removal(line)
            mapped_kind = _map_kind(remove_kind)
            if mapped_kind not in set(port.DEF_KINDS) | set(port.REF_KINDS):
                raise unknown_statement_error(
                    package_name=package_name,
                    source_path=source_path,
                    definition_kind="port def",
                    definition_name=name,
                    line=line,
                )
            if _is_reference_kind(mapped_kind):
                port.remove_refs(mapped_kind).add(remove_key)
            else:
                port.remove_defs(mapped_kind).add(remove_key)
        elif strict:
            raise unknown_statement_error(
                package_name=package_name,
                source_path=source_path,
                definition_kind="port def",
                definition_name=name,
                line=line,
            )
        pending_doc = None

    port.doc = port_doc
    return port


def parse_requirements(
    body: str, source_path: Path, package_name: str
) -> Dict[str, SysMLRequirementDefinition]:
    req_defs: Dict[str, SysMLRequirementDefinition] = {}
    if re.search(r"comment\s+[A-Za-z0-9_]+\s*/\*", body):
        raise ValueError(
            "Comment-based requirements are not supported; use requirement def/requirement syntax"
        )

    for name, base_name, block in extract_requirement_blocks(body):
        text: Optional[str] = None
        for kind, payload in iter_block_items(block):
            if kind == "doc":
                text = payload
                break
        req_def = SysMLRequirementDefinition(
            name=name,
            specializes=base_name,
            source_file=source_path.name,
        )
        if text is not None:
            req_def.add_def(
                NodeType.Attribute,
                "text",
                SysMLAttribute.from_literal(name="text", value=text),
            )
        req_defs[name] = req_def

    top_level_req_usage = _find_top_level_requirement_usage(body)
    if top_level_req_usage is not None:
        raise ValueError(
            "Requirement usage must be declared inside part def or port def blocks "
            f"in package {package_name} ({source_path}): {top_level_req_usage}"
        )
    return req_defs


def _find_top_level_requirement_usage(body: str) -> Optional[str]:
    depth = 0
    for raw_line in body.splitlines():
        line = strip_inline_comment(raw_line).strip()
        if not line:
            depth += raw_line.count("{") - raw_line.count("}")
            continue
        if depth == 0 and line.startswith("requirement ") and not line.startswith("requirement def "):
            return line
        depth += raw_line.count("{") - raw_line.count("}")
    return None
