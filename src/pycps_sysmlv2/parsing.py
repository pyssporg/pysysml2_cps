"""Parsing logic for lightweight SysML v2 folder parsing."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any, Dict, Iterator, List, Optional, Tuple

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


def _connection_key(connection: SysMLConnection) -> str:
    return (
        f"{connection.src_component}.{connection.src_port}->"
        f"{connection.dst_component}.{connection.dst_port}"
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
        name=package_name or "Package",
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
    items: Dict[str, Dict[str, object]] = {
        kind: {} for kind in SysMLPartDefinition.artifact_kinds
    }
    redefines_items: Dict[str, Dict[str, object]] = {
        kind: {} for kind in SysMLPartDefinition.artifact_kinds
    }
    remove_items = {kind: set() for kind in SysMLPartDefinition.artifact_kinds}
    pending_doc: Optional[str] = None
    part_doc: Optional[str] = None

    for kind, payload in _iter_block_items(block):
        if kind == "doc":
            has_members = any(items[k] for k in SysMLPartDefinition.artifact_kinds)
            if part_doc is None and not has_members:
                part_doc = payload
            else:
                pending_doc = payload
            continue

        line = strip_inline_comment(payload)
        if not line:
            continue

        if line.startswith("attribute "):
            attr = _parse_attribute(line, pending_doc)
            items["attributes"][attr.name] = attr
        elif line.startswith("in port "):
            port = _parse_port_endpoint("in", line, pending_doc)
            items["ports"][port.name] = port
        elif line.startswith("out port "):
            port = _parse_port_endpoint("out", line, pending_doc)
            items["ports"][port.name] = port
        elif line.startswith("part "):
            part = _parse_part_reference(line, pending_doc)
            items["parts"][part.name] = part
        elif line.startswith("connect "):
            connection = _parse_connection(line)
            items["connections"][_connection_key(connection)] = connection
        elif line.startswith("redefines "):
            replacement = _parse_replacement(line, pending_doc)
            redefines_items[replacement[0]][replacement[1].name] = replacement[1]
        elif line.startswith("remove "):
            remove_kind, remove_key = _parse_removal(line)
            remove_items[remove_kind].add(remove_key)
        elif strict:
            raise _unknown_statement_error(
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
        items=items,
        redefines_items=redefines_items,
        remove_items=remove_items,
    )
    part.declared_items = {
        kind: dict(values) for kind, values in items.items()
    }
    return part


def _parse_port_block(
    name: str, block: str, source_path: Path, package_name: str, strict: bool
) -> SysMLPortDefinition:
    items: Dict[str, Dict[str, object]] = {
        kind: {} for kind in SysMLPortDefinition.artifact_kinds
    }
    port_doc: Optional[str] = None
    pending_doc: Optional[str] = None

    for kind, payload in _iter_block_items(block):
        if kind == "doc":
            has_members = any(items[k] for k in SysMLPortDefinition.artifact_kinds)
            if port_doc is None and not has_members:
                port_doc = payload
            else:
                pending_doc = payload
            continue

        line = strip_inline_comment(payload)
        if not line:
            continue
        if line.startswith("attribute "):
            attr = _parse_attribute(line, pending_doc)
            items["attributes"][attr.name] = attr
        elif strict:
            raise _unknown_statement_error(
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
        source_file=source_path.name,
        items=items,
        redefines_items={kind: {} for kind in SysMLPortDefinition.artifact_kinds},
        remove_items={kind: set() for kind in SysMLPortDefinition.artifact_kinds},
    )
    port.declared_items = {
        kind: dict(values) for kind, values in items.items()
    }
    return port


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


def _parse_replacement(
    line: str, doc: Optional[str]
) -> Tuple[str, object]:
    if line.startswith("redefines "):
        content = line[len("redefines ") :].strip()
    else:
        raise ValueError(f"Malformed redefines statement: {line}")
    if content.startswith("attribute "):
        return ("attributes", _parse_attribute(content, doc))
    if content.startswith("in port "):
        return ("ports", _parse_port_endpoint("in", content, doc))
    if content.startswith("out port "):
        return ("ports", _parse_port_endpoint("out", content, doc))
    if content.startswith("part "):
        return ("parts", _parse_part_reference(content, doc))
    raise ValueError(f"Malformed redefines statement: {line}")


def _parse_removal(
    line: str,
) -> Tuple[str, str]:
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
    if content.startswith("connect "):
        if not content.endswith(";"):
            content = f"{content};"
        return ("connections", _connection_key(_parse_connection(content)))
    raise ValueError(f"Malformed remove statement: {line}")


def _attach_port_definitions(
    parts: Dict[str, SysMLPartDefinition], port_defs: Dict[str, SysMLPortDefinition]
) -> None:
    for part in parts.values():
        for port in part.items.get("ports", {}).values():
            port.port_def = port_defs.get(port.port_name)
            if port.port_def is None:
                raise ValueError(
                    f"Port definition not found for {part.name}.{port.name}: {port.port_name}"
                )


def _attach_part_definitions(parts: Dict[str, SysMLPartDefinition]) -> None:
    for part in parts.values():
        for subpart in part.items.get("parts", {}).values():
            subpart.part_def = parts.get(subpart.part_name)


def _attach_connection_definitions(parts: Dict[str, SysMLPartDefinition]) -> None:

    for part in parts.values():
        part_map = part.items.get("parts", {})
        for c in part.items.get("connections", {}).values():
            if c.src_component not in part_map:
                raise ValueError(
                    f"Subpart not found for connection: {part.name}.{c.src_component}"
                )
            if c.dst_component not in part_map:
                raise ValueError(
                    f"Subpart not found for connection: {part.name}.{c.dst_component}"
                )

            c.src_part_def = part_map[c.src_component].part_def
            c.dst_part_def = part_map[c.dst_component].part_def
            if c.src_part_def is None:
                raise ValueError(
                    f"Part definition not found for subpart {part.name}.{c.src_component}"
                )
            if c.dst_part_def is None:
                raise ValueError(
                    f"Part definition not found for subpart {part.name}.{c.dst_component}"
                )

            src_ports = c.src_part_def.items.get("ports", {})
            dst_ports = c.dst_part_def.items.get("ports", {})
            if c.src_port not in src_ports:
                raise ValueError(
                    f"Port not found for connection: {c.src_part_def.name}.{c.src_port}"
                )
            if c.dst_port not in dst_ports:
                raise ValueError(
                    f"Port not found for connection: {c.dst_part_def.name}.{c.dst_port}"
                )

            c.src_port_def = src_ports[c.src_port].port_def
            c.dst_port_def = dst_ports[c.dst_port].port_def
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
                name=usage_name,
                source_file=source_path.name,
                items={"text": {"text": req_defs[target_def]}},
                redefines_items={"text": {}},
                remove_items={"text": set()},
            )
        )

    if reqs:
        return reqs

    for identifier, text in req_defs.items():
        reqs.append(
            SysMLRequirement(
                name=identifier,
                source_file=source_path.name,
                items={"text": {"text": text}},
                redefines_items={"text": {}},
                remove_items={"text": set()},
            )
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
