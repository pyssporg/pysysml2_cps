from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .base import InherenceDefinition


@dataclass
class SysMLRequirementDefinition(InherenceDefinition):
    artifact_kinds: Tuple[str, ...] = ("text",)

    @property
    def text(self) -> str:
        payload = self.items.setdefault("text", {}).setdefault("text", "")
        return str(payload)

    @text.setter
    def text(self, value: str) -> None:
        self.items.setdefault("text", {})["text"] = value
