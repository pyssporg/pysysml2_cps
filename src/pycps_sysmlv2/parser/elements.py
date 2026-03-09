"""Parsers for statements inside SysML definition blocks."""

from __future__ import annotations

import re
from typing import Any, Optional, Tuple

from ..definitions import (
    SysMLAttribute,
    SysMLConnection,
    SysMLPartReference,
    SysMLPortReference,
    SysMLRequirementReference,
    SysMLType,
)


CONNECTION_RE = re.compile(
    r"connect\s+([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)\s+to\s+([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)\s*;"
)


def connection_key(connection: SysMLConnection) -> str:
    return (
        f"{connection.src_component}.{connection.src_port}->"
        f"{connection.dst_component}.{connection.dst_port}"
    )


def parse_attribute(line: str, doc: Optional[str]) -> SysMLAttribute:
    content = line[len("attribute ") :].strip()
    if content.endswith(";"):
        content = content[:-1].strip()

    attr_type: Optional[SysMLType] = None
    value: Optional[Any] = None
    if "=" in content:
        name, value = content.split("=", 1)
        name = name.strip()
        value = SysMLAttribute._parse_literal(value)
        attr_type = SysMLType.from_value(value)
    elif ":" in content:
        name, attr_type = content.split(":", 1)
        name = name.strip()
        attr_type = SysMLType.from_string(attr_type.strip())
    else:
        name = content.strip()
    return SysMLAttribute(name=name, type=attr_type, value=value, doc=doc)


def parse_port_endpoint(direction: str, line: str, doc: Optional[str]) -> SysMLPortReference:
    content = line[len(direction) :].strip()
    if content.endswith(";"):
        content = content[:-1].strip()
    if ":" not in content:
        raise ValueError(f"Malformed port declaration: {line}")
    name, payload = content.split(":", 1)
    return SysMLPortReference(
        direction=direction,
        name=_normalize_port_name(name),
        type=payload.strip(),
        doc=doc,
    )


def parse_part_reference(line: str, doc: Optional[str]) -> SysMLPartReference:
    content = line[len("part ") :].strip()
    if content.endswith(";"):
        content = content[:-1].strip()
    if ":" not in content:
        raise ValueError(f"Malformed part reference: {line}")
    name, target = content.split(":", 1)
    return SysMLPartReference(name=name.strip(), type=target.strip(), doc=doc)


def parse_requirement_reference(line: str, doc: Optional[str]) -> SysMLRequirementReference:
    content = line[len("requirement ") :].strip()
    if content.endswith(";"):
        content = content[:-1].strip()
    if ":" in content:
        name, target = content.split(":", 1)
        req_name = name.strip()
        req_def_name = target.strip()
    else:
        req_name = content.strip()
        req_def_name = req_name
    if not req_name:
        raise ValueError(f"Malformed requirement usage: {line}")
    return SysMLRequirementReference(
        name=req_name,
        type=req_def_name,
        doc=doc,
    )


def parse_connection(line: str) -> SysMLConnection:
    match = CONNECTION_RE.fullmatch(line.strip())
    if match is None:
        raise ValueError(f"Malformed connection declaration: {line}")
    src_component = match.group(1)
    src_port = match.group(2)
    dst_component = match.group(3)
    dst_port = match.group(4)
    return SysMLConnection(
        name=f"{src_component}.{src_port}_to_{dst_component}.{dst_port}",
        src_component=src_component,
        src_port=src_port,
        dst_component=dst_component,
        dst_port=dst_port,
    )


def parse_replacement(line: str, doc: Optional[str]) -> Tuple[str, object]:
    if line.startswith("redefines "):
        content = line[len("redefines ") :].strip()
    else:
        raise ValueError(f"Malformed redefines statement: {line}")
    if content.startswith("attribute "):
        return ("attributes", parse_attribute(content, doc))
    if content.startswith("in port "):
        return ("ports", parse_port_endpoint("in", content, doc))
    if content.startswith("out port "):
        return ("ports", parse_port_endpoint("out", content, doc))
    if content.startswith("part "):
        return ("parts", parse_part_reference(content, doc))
    if content.startswith("requirement "):
        return ("requirements", parse_requirement_reference(content, doc))
    raise ValueError(f"Malformed redefines statement: {line}")


def parse_removal(line: str) -> Tuple[str, str]:
    content = line[len("remove ") :].strip()
    content_no_suffix = content[:-1].strip() if content.endswith(";") else content
    if content.startswith("attribute "):
        name = content_no_suffix[len("attribute ") :].strip()
        if not name:
            raise ValueError(f"Malformed remove attribute statement: {line}")
        return ("attributes", name)
    if content.startswith("port "):
        name = content_no_suffix[len("port ") :].strip()
        if not name:
            raise ValueError(f"Malformed remove port statement: {line}")
        return ("ports", name)
    if content.startswith("part "):
        name = content_no_suffix[len("part ") :].strip()
        if not name:
            raise ValueError(f"Malformed remove part statement: {line}")
        return ("parts", name)
    if content.startswith("requirement "):
        name = content_no_suffix[len("requirement ") :].strip()
        if not name:
            raise ValueError(f"Malformed remove requirement statement: {line}")
        return ("requirements", name)
    if content.startswith("connect "):
        if not content.endswith(";"):
            content = f"{content};"
        return ("connections", connection_key(parse_connection(content)))
    raise ValueError(f"Malformed remove statement: {line}")


def _normalize_port_name(name: str) -> str:
    name = name.strip()
    if name.startswith("port "):
        return name[len("port ") :].strip()
    return name
