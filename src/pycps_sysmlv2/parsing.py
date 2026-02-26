"""Parsing logic for lightweight SysML v2 folder parsing."""

from __future__ import annotations

from pathlib import Path
import copy
import re
from typing import Dict, Iterator, List, Optional, Set, Tuple

from .definitions import (
    SysMLArchitecture,
    SysMLType,
    SysMLAttribute,
    SysMLConnection,
    SysMLPartDefinition,
    SysMLPartReference,
    SysMLPortDefinition,
    SysMLPortReference,
    SysMLRequirement,
)
from .parser_utils import collect_block, normalize_doc, strip_inline_comment


class SysMLFolderParser:
    """Parse and merge all `.sysml` files within a directory."""

    def __init__(self, folder: Path | str):
        self.folder = Path(folder)
        if not self.folder.is_dir():
            raise FileNotFoundError(f"SysML folder not found: {self.folder}")

    def parse(self) -> SysMLArchitecture:
        files = sorted(self.folder.glob("*.sysml"))
        if not files:
            raise FileNotFoundError(f"No .sysml files found under {self.folder}")

        part_defs: Dict[str, SysMLPartDefinition] = {}
        port_defs: Dict[str, SysMLPortDefinition] = {}
        requirements: List[SysMLRequirement] = []
        package_name: Optional[str] = None

        for path in files:
            text = path.read_text()
            pkg, body = _extract_package_body(text, path)
            if package_name is None:
                package_name = pkg
            elif pkg != package_name:
                raise ValueError(
                    f"Mismatched package names: {package_name} vs {pkg} in {path}"
                )

            for name, base_name, block in _extract_part_blocks(body):
                if name in part_defs:
                    raise ValueError(f"Duplicate part definition for {name} in {path}")
                part_defs[name] = _parse_part_block(name, block, base_name)

            for name, block in _extract_named_blocks(body, "port def"):
                if name in port_defs:
                    raise ValueError(f"Duplicate port definition for {name} in {path}")
                port_defs[name] = _parse_port_block(name, block)

            requirements.extend(_parse_requirements(body))

        _attach_base_part_definitions(part_defs)
        _resolve_part_inheritance(part_defs)
        _attach_port_definitions(part_defs, port_defs)
        _attach_part_definitions(part_defs)

        _attach_connection_definitions(part_defs, port_defs)
        return SysMLArchitecture(
            package=package_name or "Package",
            part_definitions=part_defs,
            port_definitions=port_defs,
            requirements=requirements,
        )


def load_architecture(folder: Path | str) -> SysMLArchitecture:
    path = Path(folder)
    if path.is_file():
        path = path.parent
    return SysMLFolderParser(path).parse()


def load_system(folder: Path | str, system_part: str):
    a = load_architecture(folder)
    if system_part not in a.part_definitions:
        raise KeyError(f"Part not found: {system_part}")
    return a.part_definitions[system_part]


_PACKAGE_RE = re.compile(r"package\s+([A-Za-z0-9_]+)\s*\{", re.MULTILINE)
_CONNECTION_RE = re.compile(
    r"connect\s+([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)\s+to\s+([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)\s*;"
)


def _extract_package_body(text: str, path: Path) -> Tuple[str, str]:
    match = _PACKAGE_RE.search(text)
    if not match:
        raise ValueError(f"No package declaration found in {path}")
    pkg_name = match.group(1)
    brace_start = match.end() - 1
    body, _ = collect_block(text, brace_start)
    return pkg_name, body


def _extract_named_blocks(body: str, keyword: str) -> List[Tuple[str, str]]:
    pattern = re.compile(rf"{keyword}\s+([A-Za-z0-9_]+)\s*\{{", re.MULTILINE)
    blocks: List[Tuple[str, str]] = []
    idx = 0
    while True:
        match = pattern.search(body, idx)
        if not match:
            break
        name = match.group(1)
        brace_start = match.end() - 1
        block, new_idx = collect_block(body, brace_start)
        blocks.append((name, block))
        idx = new_idx
    return blocks


def _extract_part_blocks(body: str) -> List[Tuple[str, Optional[str], str]]:
    pattern = re.compile(
        r"part def\s+([A-Za-z0-9_]+)(?:\s*:\s*([A-Za-z0-9_]+))?\s*\{", re.MULTILINE
    )
    blocks: List[Tuple[str, Optional[str], str]] = []
    idx = 0
    while True:
        match = pattern.search(body, idx)
        if not match:
            break
        name = match.group(1)
        base_name = match.group(2)
        brace_start = match.end() - 1
        block, new_idx = collect_block(body, brace_start)
        blocks.append((name, base_name, block))
        idx = new_idx
    return blocks


def _parse_part_block(
    name: str, block: str, base_part_name: Optional[str]
) -> SysMLPartDefinition:
    attributes: Dict[str, SysMLAttribute] = {}
    ports: Dict[str, SysMLPortReference] = {}
    parts: Dict[str, SysMLPartReference] = {}
    connections: List[SysMLConnection] = []
    replace_attributes: Dict[str, SysMLAttribute] = {}
    replace_ports: Dict[str, SysMLPortReference] = {}
    replace_parts: Dict[str, SysMLPartReference] = {}
    remove_attributes: Set[str] = set()
    remove_ports: Set[str] = set()
    remove_parts: Set[str] = set()
    remove_connections: List[SysMLConnection] = []
    pending_doc: Optional[str] = None
    part_doc: Optional[str] = None

    for kind, payload in _iter_block_items(block):
        if kind == "doc":
            if part_doc is None and not attributes and not ports and not parts:
                part_doc = payload
            else:
                pending_doc = payload
            continue

        line = strip_inline_comment(payload)
        if not line:
            continue

        if line.startswith("attribute "):
            attr = _parse_attribute(line, pending_doc)
            attributes[attr.name] = attr
        elif line.startswith("in port "):
            port = _parse_port_endpoint("in", line, pending_doc)
            ports[port.name] = port
        elif line.startswith("out port "):
            port = _parse_port_endpoint("out", line, pending_doc)
            ports[port.name] = port
        elif line.startswith("part "):
            part = _parse_part_reference(line, pending_doc)
            parts[part.name] = part
        elif line.startswith("connect "):
            connections.append(_parse_connection(line))
        elif line.startswith("replace "):
            (
                replacement_attr,
                replacement_port,
                replacement_part,
            ) = _parse_replacement(line, pending_doc)
            if replacement_attr is not None:
                replace_attributes[replacement_attr.name] = replacement_attr
            if replacement_port is not None:
                replace_ports[replacement_port.name] = replacement_port
            if replacement_part is not None:
                replace_parts[replacement_part.name] = replacement_part
        elif line.startswith("remove "):
            (
                remove_attribute,
                remove_port,
                remove_part,
                remove_connection,
            ) = _parse_removal(line)
            if remove_attribute is not None:
                remove_attributes.add(remove_attribute)
            if remove_port is not None:
                remove_ports.add(remove_port)
            if remove_part is not None:
                remove_parts.add(remove_part)
            if remove_connection is not None:
                remove_connections.append(remove_connection)

        pending_doc = None

    return SysMLPartDefinition(
        name=name,
        doc=part_doc,
        base_part_name=base_part_name,
        attributes=attributes,
        ports=ports,
        parts=parts,
        connections=connections,
        replace_attributes=replace_attributes,
        replace_ports=replace_ports,
        replace_parts=replace_parts,
        remove_attributes=remove_attributes,
        remove_ports=remove_ports,
        remove_parts=remove_parts,
        remove_connections=remove_connections,
    )


def _parse_port_block(name: str, block: str) -> SysMLPortDefinition:
    attributes: Dict[str, SysMLAttribute] = {}
    port_doc: Optional[str] = None
    pending_doc: Optional[str] = None

    for kind, payload in _iter_block_items(block):
        if kind == "doc":
            if port_doc is None and not attributes:
                port_doc = payload
            else:
                pending_doc = payload
            continue

        line = strip_inline_comment(payload)
        if not line:
            continue
        if line.startswith("attribute "):
            attr = _parse_attribute(line, pending_doc)
            attributes[attr.name] = attr
        pending_doc = None

    return SysMLPortDefinition(name=name, doc=port_doc, attributes=attributes)


def _parse_attribute(line: str, doc: Optional[str]) -> SysMLAttribute:
    content = line[len("attribute ") :].strip()
    if content.endswith(";"):
        content = content[:-1].strip()

    attr_type: Optional[str] = None
    value: Optional[str] = None
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


def _normalize_port_name(name: str) -> str:
    name = name.strip()
    if name.startswith("port "):
        return name[len("port ") :].strip()
    return name


def _parse_port_endpoint(
    direction: str, line: str, doc: Optional[str]
) -> SysMLPortReference:
    content = line[len(direction) :].strip()
    if content.endswith(";"):
        content = content[:-1].strip()
    if ":" not in content:
        raise ValueError(f"Malformed port declaration: {line}")
    name, payload = content.split(":", 1)
    return SysMLPortReference(
        direction=direction,
        name=_normalize_port_name(name),
        port_name=payload.strip(),
        doc=doc,
    )


def _parse_part_reference(line: str, doc: Optional[str]) -> SysMLPartReference:
    content = line[len("part ") :].strip()
    if content.endswith(";"):
        content = content[:-1].strip()
    if ":" not in content:
        raise ValueError(f"Malformed part reference: {line}")
    name, target = content.split(":", 1)
    return SysMLPartReference(name=name.strip(), part_name=target.strip(), doc=doc)


def _parse_connection(line: str) -> SysMLConnection:
    match = _CONNECTION_RE.fullmatch(line.strip())
    if match is None:
        raise ValueError(f"Malformed connection declaration: {line}")
    return SysMLConnection(
        src_component=match.group(1),
        src_port=match.group(2),
        dst_component=match.group(3),
        dst_port=match.group(4),
    )


def _parse_replacement(
    line: str, doc: Optional[str]
) -> Tuple[
    Optional[SysMLAttribute],
    Optional[SysMLPortReference],
    Optional[SysMLPartReference],
]:
    content = line[len("replace ") :].strip()
    if content.startswith("attribute "):
        return (_parse_attribute(content, doc), None, None)
    if content.startswith("in port "):
        return (None, _parse_port_endpoint("in", content, doc), None)
    if content.startswith("out port "):
        return (None, _parse_port_endpoint("out", content, doc), None)
    if content.startswith("part "):
        return (None, None, _parse_part_reference(content, doc))
    raise ValueError(f"Malformed replace statement: {line}")


def _parse_removal(
    line: str,
) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[SysMLConnection]]:
    content = line[len("remove ") :].strip()
    content_no_suffix = content[:-1].strip() if content.endswith(";") else content
    if content.startswith("attribute "):
        name = content_no_suffix[len("attribute ") :].strip()
        if not name:
            raise ValueError(f"Malformed remove attribute statement: {line}")
        return (name, None, None, None)
    if content.startswith("port "):
        name = content_no_suffix[len("port ") :].strip()
        if not name:
            raise ValueError(f"Malformed remove port statement: {line}")
        return (None, name, None, None)
    if content.startswith("part "):
        name = content_no_suffix[len("part ") :].strip()
        if not name:
            raise ValueError(f"Malformed remove part statement: {line}")
        return (None, None, name, None)
    if content.startswith("connect "):
        if not content.endswith(";"):
            content = f"{content};"
        return (None, None, None, _parse_connection(content))
    raise ValueError(f"Malformed remove statement: {line}")


def _attach_base_part_definitions(parts: Dict[str, SysMLPartDefinition]) -> None:
    for part in parts.values():
        if part.base_part_name is None:
            continue
        part.base_part_def = parts.get(part.base_part_name)
        if part.base_part_def is None:
            raise ValueError(
                f"Base part definition not found for {part.name}: {part.base_part_name}"
            )


def _resolve_part_inheritance(parts: Dict[str, SysMLPartDefinition]) -> None:
    visited: Set[str] = set()
    visiting: Set[str] = set()
    stack: List[str] = []

    def resolve(name: str) -> None:
        if name in visited:
            return
        if name in visiting:
            start = stack.index(name)
            cycle = " -> ".join(stack[start:] + [name])
            raise ValueError(f"Inheritance cycle detected: {cycle}")

        visiting.add(name)
        stack.append(name)

        part = parts[name]
        if part.base_part_name is not None:
            if part.base_part_name not in parts:
                raise ValueError(
                    f"Base part definition not found for {part.name}: {part.base_part_name}"
                )
            resolve(part.base_part_name)
            _merge_with_base(part, parts[part.base_part_name])

        stack.pop()
        visiting.remove(name)
        visited.add(name)

    for name in parts:
        resolve(name)


def _merge_with_base(
    part: SysMLPartDefinition, base: SysMLPartDefinition
) -> None:
    merged_attributes = copy.deepcopy(base.attributes)
    merged_ports = copy.deepcopy(base.ports)
    merged_parts = copy.deepcopy(base.parts)
    merged_connections = copy.deepcopy(base.connections)

    for attr_name in part.remove_attributes:
        if attr_name not in merged_attributes:
            raise ValueError(f"Cannot remove unknown attribute {part.name}.{attr_name}")
        del merged_attributes[attr_name]
    for port_name in part.remove_ports:
        if port_name not in merged_ports:
            raise ValueError(f"Cannot remove unknown port {part.name}.{port_name}")
        del merged_ports[port_name]
    for part_name in part.remove_parts:
        if part_name not in merged_parts:
            raise ValueError(f"Cannot remove unknown part {part.name}.{part_name}")
        del merged_parts[part_name]
    for connection in part.remove_connections:
        if not _remove_connection(merged_connections, connection):
            raise ValueError(f"Cannot remove unknown connection in {part.name}: {connection}")

    for attr_name, attr in part.replace_attributes.items():
        if attr_name not in merged_attributes:
            raise ValueError(f"Cannot replace unknown attribute {part.name}.{attr_name}")
        merged_attributes[attr_name] = attr
    for port_name, port in part.replace_ports.items():
        if port_name not in merged_ports:
            raise ValueError(f"Cannot replace unknown port {part.name}.{port_name}")
        merged_ports[port_name] = port
    for part_name, subpart in part.replace_parts.items():
        if part_name not in merged_parts:
            raise ValueError(f"Cannot replace unknown part {part.name}.{part_name}")
        merged_parts[part_name] = subpart
    for attr_name, attr in part.attributes.items():
        if attr_name in merged_attributes:
            raise ValueError(
                f"Attribute name collision in {part.name}: {attr_name} (use replace attribute)"
            )
        merged_attributes[attr_name] = attr
    for port_name, port in part.ports.items():
        if port_name in merged_ports:
            raise ValueError(
                f"Port name collision in {part.name}: {port_name} (use replace in/out port)"
            )
        merged_ports[port_name] = port
    for part_name, subpart in part.parts.items():
        if part_name in merged_parts:
            raise ValueError(
                f"Part name collision in {part.name}: {part_name} (use replace part)"
            )
        merged_parts[part_name] = subpart
    for connection in part.connections:
        if _contains_connection(merged_connections, connection):
            raise ValueError(
                f"Connection already exists in {part.name}: "
                f"{connection.src_component}.{connection.src_port} to "
                f"{connection.dst_component}.{connection.dst_port} "
                f"(use remove connect first)"
            )
        merged_connections.append(connection)

    part.attributes = merged_attributes
    part.ports = merged_ports
    part.parts = merged_parts
    part.connections = merged_connections


def _connection_key(connection: SysMLConnection) -> Tuple[str, str, str, str]:
    return (
        connection.src_component,
        connection.src_port,
        connection.dst_component,
        connection.dst_port,
    )


def _remove_connection(
    target_connections: List[SysMLConnection], connection: SysMLConnection
) -> bool:
    key = _connection_key(connection)
    for idx, candidate in enumerate(target_connections):
        if _connection_key(candidate) == key:
            del target_connections[idx]
            return True
    return False


def _contains_connection(
    target_connections: List[SysMLConnection], connection: SysMLConnection
) -> bool:
    key = _connection_key(connection)
    return any(_connection_key(candidate) == key for candidate in target_connections)


def _attach_port_definitions(
    parts: Dict[str, SysMLPartDefinition], port_defs: Dict[str, SysMLPortDefinition]
) -> None:
    for part in parts.values():
        for port in part.ports.values():
            port.port_def = port_defs.get(port.port_name)
            if port.port_def is None:
                raise ValueError(
                    f"Port definition not found for {part.name}.{port.name}: {port.port_name}"
                )


def _attach_part_definitions(parts: Dict[str, SysMLPartDefinition]) -> None:
    for part in parts.values():
        for subpart in part.parts.values():
            subpart.part_def = parts.get(subpart.part_name)


def _attach_connection_definitions(
    parts: Dict[str, SysMLPartDefinition], ports: Dict[str, SysMLPortDefinition]
) -> None:

    for part in parts.values():
        for c in part.connections:
            if c.src_component not in part.parts:
                raise ValueError(
                    f"Subpart not found for connection: {part.name}.{c.src_component}"
                )
            if c.dst_component not in part.parts:
                raise ValueError(
                    f"Subpart not found for connection: {part.name}.{c.dst_component}"
                )

            c.src_part_def = part.parts[c.src_component].part_def
            c.dst_part_def = part.parts[c.dst_component].part_def
            if c.src_part_def is None:
                raise ValueError(
                    f"Part definition not found for subpart {part.name}.{c.src_component}"
                )
            if c.dst_part_def is None:
                raise ValueError(
                    f"Part definition not found for subpart {part.name}.{c.dst_component}"
                )

            if c.src_port not in c.src_part_def.ports:
                raise ValueError(
                    f"Port not found for connection: {c.src_part_def.name}.{c.src_port}"
                )
            if c.dst_port not in c.dst_part_def.ports:
                raise ValueError(
                    f"Port not found for connection: {c.dst_part_def.name}.{c.dst_port}"
                )

            c.src_port_def = c.src_part_def.ports[c.src_port].port_def
            c.dst_port_def = c.dst_part_def.ports[c.dst_port].port_def
            if c.src_port_def is None:
                raise ValueError(
                    f"Port definition not found for connection endpoint: "
                    f"{c.src_part_def.name}.{c.src_port}"
                )
            if c.dst_port_def is None:
                raise ValueError(
                    f"Port definition not found for connection endpoint: "
                    f"{c.dst_part_def.name}.{c.dst_port}"
                )

def _iter_block_items(block: str) -> Iterator[Tuple[str, str]]:
    lines = block.splitlines()
    idx = 0
    while idx < len(lines):
        stripped = lines[idx].strip()
        idx += 1
        if not stripped:
            continue
        if stripped.startswith("doc"):
            doc_lines = [stripped]
            while "*/" not in stripped:
                if idx >= len(lines):
                    raise ValueError("Unterminated doc comment in SysML block")
                stripped = lines[idx].strip()
                doc_lines.append(stripped)
                idx += 1
            yield ("doc", normalize_doc(" ".join(doc_lines)))
        else:
            yield ("stmt", stripped)


def _parse_requirements(body: str) -> List[SysMLRequirement]:
    reqs: List[SysMLRequirement] = []
    pattern = re.compile(r"comment\s+([A-Za-z0-9_]+)\s*/\*\s*(.*?)\s*\*/", re.DOTALL)
    for match in pattern.finditer(body):
        identifier = match.group(1)
        text = re.sub(r"\s+", " ", match.group(2).strip())
        reqs.append(SysMLRequirement(identifier=identifier, text=text))
    return reqs
