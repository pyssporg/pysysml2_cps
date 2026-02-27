"""Parser error constructors."""

from __future__ import annotations

from pathlib import Path


def unknown_statement_error(
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
