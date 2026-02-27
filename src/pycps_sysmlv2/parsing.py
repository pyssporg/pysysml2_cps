"""Compatibility facade for parser entrypoints."""

from __future__ import annotations

from .parser import SysMLFolderParser, load_architecture, load_system

__all__ = ["SysMLFolderParser", "load_architecture", "load_system"]
