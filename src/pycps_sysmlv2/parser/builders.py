"""Builders for SysML definitions parsed from blocks."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Dict, Optional

from ..definitions import (
    SysMLPartDefinition,
    SysMLPortDefinition,
    SysMLRequirementDefinition,
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


def parse_part_block(
    name: str,
    block: str,
    base_part_name: Optional[str],
    source_path: Path,
    package_name: str,
    strict: bool,
) -> SysMLPartDefinition:
    items: Dict[str, Dict[str, object]] = {
        kind: {} for kind in SysMLPartDefinition.reference_kinds
    }
    redefines_items: Dict[str, Dict[str, object]] = {
        kind: {} for kind in SysMLPartDefinition.reference_kinds
    }
    remove_items = {kind: set() for kind in SysMLPartDefinition.reference_kinds}
    pending_doc: Optional[str] = None
    part_doc: Optional[str] = None

    for kind, payload in iter_block_items(block):
        if kind == "doc":
            has_members = any(items[k] for k in SysMLPartDefinition.reference_kinds)
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
            items["attributes"][attr.name] = attr
        elif line.startswith("in port "):
            port = parse_port_endpoint("in", line, pending_doc)
            items["ports"][port.name] = port
        elif line.startswith("out port "):
            port = parse_port_endpoint("out", line, pending_doc)
            items["ports"][port.name] = port
        elif line.startswith("part "):
            part = parse_part_reference(line, pending_doc)
            items["parts"][part.name] = part
        elif line.startswith("requirement "):
            requirement = parse_requirement_reference(line, pending_doc)
            items["requirements"][requirement.name] = requirement
        elif line.startswith("connect "):
            connection = parse_connection(line)
            items["connections"][connection_key(connection)] = connection
        elif line.startswith("redefines "):
            replacement_kind, replacement_value = parse_replacement(line, pending_doc)
            redefines_items[replacement_kind][replacement_value.name] = replacement_value
        elif line.startswith("remove "):
            remove_kind, remove_key = parse_removal(line)
            remove_items[remove_kind].add(remove_key)
        elif strict:
            raise unknown_statement_error(
                package_name=package_name,
                source_path=source_path,
                definition_kind="part def",
                definition_name=name,
                line=line,
            )

        pending_doc = None

    part = SysMLPartDefinition(
        name=name,
        doc=part_doc,
        specializes=base_part_name,
        source_file=source_path.name,
        _refs=items,
        redefines_references=redefines_items,
        remove_references=remove_items,
    )
    part.declared_items = {kind: dict(values) for kind, values in items.items()}
    return part


def parse_port_block(
    name: str,
    block: str,
    base_port_name: Optional[str],
    source_path: Path,
    package_name: str,
    strict: bool,
) -> SysMLPortDefinition:
    items: Dict[str, Dict[str, object]] = {
        kind: {} for kind in SysMLPortDefinition.reference_kinds
    }
    redefines_items: Dict[str, Dict[str, object]] = {
        kind: {} for kind in SysMLPortDefinition.reference_kinds
    }
    remove_items = {kind: set() for kind in SysMLPortDefinition.reference_kinds}
    port_doc: Optional[str] = None
    pending_doc: Optional[str] = None

    for kind, payload in iter_block_items(block):
        if kind == "doc":
            has_members = any(items[k] for k in SysMLPortDefinition.reference_kinds)
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
            items["attributes"][attr.name] = attr
        elif line.startswith("requirement "):
            requirement = parse_requirement_reference(line, pending_doc)
            items["requirements"][requirement.name] = requirement
        elif line.startswith("redefines "):
            replacement_kind, replacement_value = parse_replacement(line, pending_doc)
            if replacement_kind not in items:
                raise unknown_statement_error(
                    package_name=package_name,
                    source_path=source_path,
                    definition_kind="port def",
                    definition_name=name,
                    line=line,
                )
            redefines_items[replacement_kind][replacement_value.name] = replacement_value
        elif line.startswith("remove "):
            remove_kind, remove_key = parse_removal(line)
            if remove_kind not in items:
                raise unknown_statement_error(
                    package_name=package_name,
                    source_path=source_path,
                    definition_kind="port def",
                    definition_name=name,
                    line=line,
                )
            remove_items[remove_kind].add(remove_key)
        elif strict:
            raise unknown_statement_error(
                package_name=package_name,
                source_path=source_path,
                definition_kind="port def",
                definition_name=name,
                line=line,
            )
        pending_doc = None

    port = SysMLPortDefinition(
        name=name,
        doc=port_doc,
        specializes=base_port_name,
        source_file=source_path.name,
        _refs=items,
        redefines_references=redefines_items,
        remove_references=remove_items,
    )
    port.declared_items = {kind: dict(values) for kind, values in items.items()}
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
        items = {kind: {} for kind in SysMLRequirementDefinition.reference_kinds}
        if text is not None:
            items["text"]["text"] = text
        req_def = SysMLRequirementDefinition(
            name=name,
            specializes=base_name,
            source_file=source_path.name,
            _refs=items,
            redefines_references={kind: {} for kind in SysMLRequirementDefinition.reference_kinds},
            remove_references={kind: set() for kind in SysMLRequirementDefinition.reference_kinds},
        )
        req_def.declared_items = {kind: dict(values) for kind, values in items.items()}
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
