"""Block extraction and lexical helpers for SysML parsing."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Iterator, List, Optional, Tuple

from ..parser_utils import collect_block, normalize_doc, strip_inline_comment


PACKAGE_RE = re.compile(r"package\s+([A-Za-z0-9_]+)\s*\{", re.MULTILINE)


def extract_package_body(text: str, path: Path) -> Tuple[str, str]:
    match = PACKAGE_RE.search(text)
    if not match:
        raise ValueError(f"No package declaration found in {path}")
    pkg_name = match.group(1)
    brace_start = match.end() - 1
    body, _ = collect_block(text, brace_start)
    return pkg_name, body


def extract_named_blocks(body: str, keyword: str) -> List[Tuple[str, str]]:
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


def extract_part_blocks(body: str) -> List[Tuple[str, Optional[str], str]]:
    pattern = re.compile(
        r"part def\s+([A-Za-z0-9_]+)(?:\s*specializes\s*([A-Za-z0-9_]+))?\s*\{",
        re.MULTILINE,
    )
    return _extract_specializable_blocks(body, pattern)


def extract_port_blocks(body: str) -> List[Tuple[str, Optional[str], str]]:
    pattern = re.compile(
        r"port def\s+([A-Za-z0-9_]+)(?:\s*specializes\s*([A-Za-z0-9_]+))?\s*\{",
        re.MULTILINE,
    )
    return _extract_specializable_blocks(body, pattern)


def extract_requirement_blocks(body: str) -> List[Tuple[str, Optional[str], str]]:
    pattern = re.compile(
        r"requirement def\s+([A-Za-z0-9_]+)(?:\s*specializes\s*([A-Za-z0-9_]+))?\s*\{",
        re.MULTILINE,
    )
    return _extract_specializable_blocks(body, pattern)


def _extract_specializable_blocks(
    body: str, pattern: re.Pattern[str]
) -> List[Tuple[str, Optional[str], str]]:
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


def iter_block_items(block: str) -> Iterator[Tuple[str, str]]:
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
            yield ("stmt", strip_inline_comment(stripped))
