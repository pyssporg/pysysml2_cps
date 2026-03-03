from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from .base import InherenceDefinition
from .requirement_definition import SysMLRequirementDefinition


@dataclass
class SysMLPortDefinition(InherenceDefinition):
    artifact_kinds: Tuple[str, ...] = ("attributes", "requirements")

    @property
    def attributes(self) -> Dict[str, object]:
        return self.items.setdefault("attributes", {})

    @property
    def requirements(self) -> Dict[str, object]:
        return self.items.setdefault("requirements", {})

    def add_requirement(
        self,
        name: str,
        requirement_name: Optional[str] = None,
        requirement_def: Optional[SysMLRequirementDefinition] = None,
        doc: Optional[str] = None,
    ) -> "SysMLRequirementReference":
        from .references import SysMLRequirementReference

        resolved_name = requirement_name or (
            requirement_def.name if requirement_def is not None else name
        )
        requirement_ref = SysMLRequirementReference(
            name=name,
            requirement_name=resolved_name,
            requirement_def=requirement_def,
            doc=doc,
        )
        self.requirements[name] = requirement_ref
        return requirement_ref

    def remove_requirement(self, name: str) -> "SysMLRequirementReference":
        if name not in self.requirements:
            raise KeyError(f"Requirement reference not found: {name}")
        return self.requirements.pop(name)  # type: ignore[return-value]
