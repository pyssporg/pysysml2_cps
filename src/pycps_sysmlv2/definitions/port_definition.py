from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from .base import InherenceDefinition
from .requirement_definition import SysMLRequirementDefinition
from .attributes import SysMLAttribute


@dataclass
class SysMLPortDefinition(InherenceDefinition):
    DEF_KINDS: tuple[str, ...] = ("attributes",)
    REF_KINDS: tuple[str, ...] = tuple()

    # Add def
    def add_attributes_def(self, key: str, reference: SysMLAttribute):
        self.add_def(kind="attributes", key=key, obj=reference)

    # Remove def
    def remove_attributes_def(self, key: str):
        self.remove_def(kind="attributes", key=key)

    # get def
    def get_attributes_def(self, key: str):
        return self.get_def(kind="attributes", key=key)
