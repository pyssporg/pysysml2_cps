"""Parsing logic for lightweight SysML v2 folder parsing."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple

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
from .inheritance import resolve_part_inheritance
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
        return _parse_sysml_files(files)


def load_architecture(folder: Path | str) -> SysMLArchitecture:
    path = Path(folder)
    if path.is_file():
        return _parse_sysml_files([path])
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


def _parse_sysml_files(files: List[Path]) -> SysMLArchitecture:
    part_defs: Dict[str, SysMLPartDefinition] = {}
    port_defs: Dict[str, SysMLPortDefinition] = {}
    requirements: List[SysMLRequirement] = []
    package_name: Optional[str] = None

    for path in files:
        text = path.read_text()
        pkg, body = _extract_package_body(text, path)
        legacy_inheritance = re.search(
            r"part def\s+[A-Za-z0-9_]+\s*:\s*[A-Za-z0-9_]+\s*\{", body
        )
        if legacy_inheritance is not None:
            raise ValueError(
                f"Legacy inheritance syntax ':' is not supported in {path}; "
                "use 'specializes' instead"
            )
        if package_name is None:
            package_name = pkg
        elif pkg != package_name:
            raise ValueError(
                f"Mismatched package names: {package_name} vs {pkg} in {path}"
            )

        for name, base_name, block in _extract_part_blocks(body):
            if name in part_defs:
                raise ValueError(f"Duplicate part definition for {name} in {path}")
            part_defs[name] = _parse_part_block(
                name=name,
                block=block,
                base_part_name=base_name,
                source_path=path,
                package_name=pkg,
                strict=True,
            )

        for name, block in _extract_named_blocks(body, "port def"):
            if name in port_defs:
                raise ValueError(f"Duplicate port definition for {name} in {path}")
            port_defs[name] = _parse_port_block(
                name=name,
                block=block,
                source_path=path,
                package_name=pkg,
                strict=True,
            )

        requirements.extend(_parse_requirements(body, source_path=path, package_name=pkg))

    resolve_part_inheritance(part_defs)
    _attach_port_definitions(part_defs, port_defs)
    _attach_part_definitions(part_defs)
    _attach_connection_definitions(part_defs)
    return SysMLArchitecture(
        package=package_name or "Package",
        part_definitions=part_defs,
        port_definitions=port_defs,
        requirements=requirements,
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
        r"part def\s+([A-Za-z0-9_]+)(?:\s*specializes\s*([A-Za-z0-9_]+))?\s*\{",
        re.MULTILINE,
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
    name: str,
    block: str,
    base_part_name: Optional[str],
    source_path: Path,
    package_name: str,
    strict: bool,
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
        elif line.startswith("redefines "):
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
        elif strict:
            raise _unknown_statement_error(
                package_name=package_name,
                source_path=source_path,
                definition_kind="part def",
                definition_name=name,
                line=line,
            )

        pending_doc = None

    return SysMLPartDefinition(
        name=name,
        doc=part_doc,
        base_part_name=base_part_name,
        source_file=source_path.name,
        attributes=attributes.copy(),
        ports=ports.copy(),
        parts=parts.copy(),
        connections=list(connections),
        declared_attributes=attributes.copy(),
        declared_ports=ports.copy(),
        declared_parts=parts.copy(),
        declared_connections=list(connections),
        replace_attributes=replace_attributes,
        replace_ports=replace_ports,
        replace_parts=replace_parts,
        remove_attributes=remove_attributes,
        remove_ports=remove_ports,
        remove_parts=remove_parts,
        remove_connections=remove_connections,
    )


def _parse_port_block(
    name: str, block: str, source_path: Path, package_name: str, strict: bool
) -> SysMLPortDefinition:
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
        elif strict:
            raise _unknown_statement_error(
                package_name=package_name,
                source_path=source_path,
                definition_kind="port def",
                definition_name=name,
                line=line,
            )
        pending_doc = None

    return SysMLPortDefinition(
        name=name, doc=port_doc, attributes=attributes, source_file=source_path.name
    )


def _parse_attribute(line: str, doc: Optional[str]) -> SysMLAttribute:
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
    if line.startswith("redefines "):
        content = line[len("redefines ") :].strip()
    else:
        raise ValueError(f"Malformed redefines statement: {line}")
    if content.startswith("attribute "):
        return (_parse_attribute(content, doc), None, None)
    if content.startswith("in port "):
        return (None, _parse_port_endpoint("in", content, doc), None)
    if content.startswith("out port "):
        return (None, _parse_port_endpoint("out", content, doc), None)
    if content.startswith("part "):
        return (None, None, _parse_part_reference(content, doc))
    raise ValueError(f"Malformed redefines statement: {line}")


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


def _attach_connection_definitions(parts: Dict[str, SysMLPartDefinition]) -> None:

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


def _parse_requirements(
    body: str, source_path: Path, package_name: str
) -> List[SysMLRequirement]:
    reqs: List[SysMLRequirement] = []
    if re.search(r"comment\s+[A-Za-z0-9_]+\s*/\*", body):
        raise ValueError(
            "Comment-based requirements are not supported; use requirement def/requirement syntax"
        )

    req_defs: Dict[str, str] = {}
    for name, block in _extract_named_blocks(body, "requirement def"):
        text = ""
        for kind, payload in _iter_block_items(block):
            if kind == "doc":
                text = payload
                break
        req_defs[name] = text

    usage_pattern = re.compile(
        r"requirement\s+([A-Za-z0-9_]+)(?:\s*:\s*([A-Za-z0-9_]+))?\s*;"
    )
    for match in usage_pattern.finditer(body):
        usage_name = match.group(1)
        target_def = match.group(2) or usage_name
        if target_def not in req_defs:
            raise ValueError(
                "Requirement usage references unknown requirement definition "
                f"{target_def} in package {package_name} ({source_path})"
            )
        reqs.append(
            SysMLRequirement(
                identifier=usage_name, text=req_defs[target_def], source_file=source_path.name
            )
        )

    if reqs:
        return reqs

    for identifier, text in req_defs.items():
        reqs.append(
            SysMLRequirement(identifier=identifier, text=text, source_file=source_path.name)
        )
    return reqs


def _unknown_statement_error(
    package_name: str,
    source_path: Path,
    definition_kind: str,
    definition_name: str,
    line: str,
) -> ValueError:
    return ValueError(
        "Unknown statement while parsing "
        f"{definition_kind} {definition_name} in package {package_name} "
        f"({source_path}): {line}"
    )
