from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .base import InherenceDefinition


@dataclass
class SysMLRequirementDefinition(InherenceDefinition):
    reference_kinds: Tuple[str, ...] = ("text",)

    @property
    def text(self) -> str:
        payload = self.references.setdefault("text", {}).setdefault("text", "")
        return str(payload)

    @text.setter
    def text(self, value: str) -> None:
        self.references.setdefault("text", {})["text"] = value
