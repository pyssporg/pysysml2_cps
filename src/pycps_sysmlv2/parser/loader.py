"""Top-level SysML file/folder loading orchestration."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Dict, List, Optional

from ..definitions import (
    SysMLPackage,
    SysMLPartDefinition,
    SysMLPortDefinition,
    SysMLRequirementDefinition,
)
from ..inheritance import (
    resolve_part_inheritance,
    resolve_port_inheritance,
    resolve_requirement_inheritance,
)
from .blocks import extract_package_body, extract_part_blocks, extract_port_blocks
from .builders import parse_part_block, parse_port_block, parse_requirements
from .linking import (
    attach_connection_definitions,
    attach_part_definitions,
    attach_port_definitions,
    attach_requirement_definitions,
)


#
class SysMLParser:
    """Parse `.sysml` file(s)."""

    def __init__(self, path: Path | str):
        """file or folder"""
        self.path = Path(path)

    def parse(self) -> SysMLPackage:
        if self.path.is_file():
            return _parse_sysml_files([self.path])

        elif self.path.is_dir():
            files = sorted(self.path.glob("*.sysml"))
            if not files:
                raise FileNotFoundError(f"No .sysml files found under {self.path}")
            return _parse_sysml_files(files)
        else:
            raise FileNotFoundError(f"No .sysml file found under {self.path}")


def _parse_sysml_files(files: List[Path]) -> SysMLPackage:
    part_defs: Dict[str, SysMLPartDefinition] = {}
    port_defs: Dict[str, SysMLPortDefinition] = {}
    requirement_defs: Dict[str, SysMLRequirementDefinition] = {}
    package_name: Optional[str] = None

    for path in files:
        text = path.read_text()
        pkg, body = extract_package_body(text, path)
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

        for name, base_name, block in extract_part_blocks(body):
            if name in part_defs:
                raise ValueError(f"Duplicate part definition for {name} in {path}")
            part_defs[name] = parse_part_block(
                name=name,
                block=block,
                base_part_name=base_name,
                source_path=path,
                package_name=pkg,
                strict=True,
            )

        for name, base_name, block in extract_port_blocks(body):
            if name in port_defs:
                raise ValueError(f"Duplicate port definition for {name} in {path}")
            port_defs[name] = parse_port_block(
                name=name,
                block=block,
                base_port_name=base_name,
                source_path=path,
                package_name=pkg,
                strict=True,
            )

        parsed_req_defs = parse_requirements(body, source_path=path, package_name=pkg)
        for name, req_def in parsed_req_defs.items():
            if name in requirement_defs:
                raise ValueError(
                    f"Duplicate requirement definition for {name} in {path}"
                )
            requirement_defs[name] = req_def

    resolve_part_inheritance(part_defs)
    resolve_port_inheritance(port_defs)
    resolve_requirement_inheritance(requirement_defs)

    attach_port_definitions(part_defs, port_defs)
    attach_part_definitions(part_defs)
    attach_connection_definitions(part_defs)
    attach_requirement_definitions(part_defs, port_defs, requirement_defs)

    return SysMLPackage(
        name=package_name or "Package",
        package=package_name or "Package",
        part_definitions=part_defs,
        port_definitions=port_defs,
        requirement_definitions=requirement_defs,
    )
