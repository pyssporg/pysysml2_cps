from __future__ import annotations

from pycps_sysmlv2 import (
    NodeType,
    SysMLConnection,
    SysMLPackage,
    SysMLParser,
    SysMLPartDefinition,
    SysMLPartReference,
    SysMLPortDefinition,
    SysMLPortReference,
    SysMLRequirementDefinition,
    SysMLRequirementReference,
)


def main() -> None:
    exported = {
        "NodeType": NodeType,
        "SysMLParser": SysMLParser,
        "SysMLPackage": SysMLPackage,
        "SysMLPartDefinition": SysMLPartDefinition,
        "SysMLPortDefinition": SysMLPortDefinition,
        "SysMLRequirementDefinition": SysMLRequirementDefinition,
        "SysMLPartReference": SysMLPartReference,
        "SysMLPortReference": SysMLPortReference,
        "SysMLRequirementReference": SysMLRequirementReference,
        "SysMLConnection": SysMLConnection,
    }
    assert all(exported.values())


if __name__ == "__main__":
    main()
