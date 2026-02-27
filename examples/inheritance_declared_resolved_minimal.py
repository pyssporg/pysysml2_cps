"""Minimal inheritance prototype for review.

This is intentionally separate from the production parser code.
It demonstrates:
- declared model (what the user wrote)
- resolved model (effective inherited result)
- redefines/remove/add merge behavior
- dynamic artifact kinds per part definition
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple


@dataclass
class DeclaredDefinition:
    name: str
    artifact_kinds: Tuple[str, ...]
    specializes: Optional[str] = None
    source_file: Optional[str] = None
    items: Dict[str, Dict[str, object]] = field(default_factory=dict)
    redefines_items: Dict[str, Dict[str, object]] = field(default_factory=dict)
    remove_items: Dict[str, set[str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for kind in self.artifact_kinds:
            self.items.setdefault(kind, {})
            self.redefines_items.setdefault(kind, {})
            self.remove_items.setdefault(kind, set())


@dataclass
class ResolvedDefinition:
    name: str
    artifact_kinds: Tuple[str, ...]
    specializes: Optional[str]
    source_file: Optional[str]
    items: Dict[str, Dict[str, object]]


def _merge_artifact_kind(
    *,
    kind: str,
    part_name: str,
    target: Dict[str, object],
    declared: DeclaredDefinition,
) -> None:
    remove_items = declared.remove_items[kind]
    redefine_items = declared.redefines_items[kind]
    add_items = declared.items[kind]
    singular = kind[:-1]

    for key in remove_items:
        if key not in target:
            raise ValueError(f"Cannot remove unknown {singular}: {part_name}.{key}")
        del target[key]

    for key, value in redefine_items.items():
        if key not in target:
            raise ValueError(f"Cannot redefine unknown {singular}: {part_name}.{key}")
        target[key] = value

    for key, value in add_items.items():
        if key in target:
            raise ValueError(
                f"{singular.capitalize()} collision in {part_name}: {key} "
                f"(use redefines {singular})"
            )
        target[key] = value


def resolve_part(
    declared: DeclaredDefinition,
    all_declared: Dict[str, DeclaredDefinition],
    cache: Dict[str, ResolvedDefinition],
) -> ResolvedDefinition:
    if declared.name in cache:
        return cache[declared.name]

    resolved_items: Dict[str, Dict[str, object]] = {
        kind: {} for kind in declared.artifact_kinds
    }
    if declared.specializes is not None:
        base = all_declared.get(declared.specializes)
        if base is None:
            raise ValueError(f"Unknown base part: {declared.name} -> {declared.specializes}")
        if base.artifact_kinds != declared.artifact_kinds:
            raise ValueError(
                f"Artifact kinds mismatch: {declared.name} and base {base.name} must match"
            )

        base_resolved = resolve_part(base, all_declared, cache)
        for kind in declared.artifact_kinds:
            resolved_items[kind] = dict(base_resolved.items[kind])

    for kind in declared.artifact_kinds:
        _merge_artifact_kind(
            kind=kind,
            part_name=declared.name,
            target=resolved_items[kind],
            declared=declared,
        )

    resolved = ResolvedDefinition(
        name=declared.name,
        artifact_kinds=declared.artifact_kinds,
        specializes=declared.specializes,
        source_file=declared.source_file,
        items=resolved_items,
    )
    cache[declared.name] = resolved
    return resolved


class SysMLEmitter:
    def __init__(self, indent: str = "  "):
        self.indent = indent

    def emit_declared_package(
        self, package_name: str, parts: Dict[str, DeclaredDefinition]
    ) -> str:
        lines = [f"package {package_name} {{"]
        for part_name in sorted(parts):
            lines.extend(self._emit_declared_part(parts[part_name], level=1))
            lines.append("")
        if lines[-1] == "":
            lines.pop()
        lines.append("}")
        return "\n".join(lines) + "\n"

    def emit_flattened_package(
        self, package_name: str, parts: Dict[str, DeclaredDefinition]
    ) -> str:
        lines = [f"package {package_name} {{"]
        cache: Dict[str, ResolvedDefinition] = {}
        for part_name in sorted(parts):
            resolved = resolve_part(parts[part_name], parts, cache)
            lines.extend(self._emit_flattened_part(resolved, level=1))
            lines.append("")
        if lines[-1] == "":
            lines.pop()
        lines.append("}")
        return "\n".join(lines) + "\n"

    def emit_declared_files(
        self, package_name: str, parts: Dict[str, DeclaredDefinition]
    ) -> Dict[str, str]:
        by_file: Dict[str, Dict[str, DeclaredDefinition]] = {}
        for part_name, part in parts.items():
            file_name = part.source_file or "generated.sysml"
            by_file.setdefault(file_name, {})[part_name] = part

        emitted: Dict[str, str] = {}
        for file_name, file_parts in sorted(by_file.items()):
            emitted[file_name] = self.emit_declared_package(package_name, file_parts)
        return emitted

    def _emit_declared_part(self, part: DeclaredDefinition, level: int) -> list[str]:
        pad = self.indent * level
        header = f"{pad}part def {part.name}"
        if part.specializes is not None:
            header += f" specializes {part.specializes}"
        header += " {"
        lines = [header]
        lines.extend(self._emit_declared_items(part, level + 1))
        lines.append(f"{pad}}}")
        return lines

    def _emit_declared_items(self, part: DeclaredDefinition, level: int) -> list[str]:
        pad = self.indent * level
        lines: list[str] = []
        for kind in part.artifact_kinds:
            singular = kind[:-1]
            for name in sorted(part.remove_items[kind]):
                lines.append(f"{pad}remove {singular} {name};")
            for name in sorted(part.redefines_items[kind]):
                value = part.redefines_items[kind][name]
                lines.append(f"{pad}redefines {singular} {name} = {self._fmt(value)};")
            for name in sorted(part.items[kind]):
                value = part.items[kind][name]
                lines.append(f"{pad}{singular} {name} = {self._fmt(value)};")
        return lines

    def _emit_flattened_part(self, part: ResolvedDefinition, level: int) -> list[str]:
        pad = self.indent * level
        lines = [f"{pad}part def {part.name} {{"]
        for kind in part.artifact_kinds:
            singular = kind[:-1]
            for name in sorted(part.items[kind]):
                value = part.items[kind][name]
                lines.append(f"{pad}{self.indent}{singular} {name} = {self._fmt(value)};")
        lines.append(f"{pad}}}")
        return lines

    def _fmt(self, value: object) -> str:
        if isinstance(value, str):
            return f"\"{value}\""
        return repr(value)


def demo() -> None:
    artifact_kinds = ("attributes", "ports")

    base = DeclaredDefinition(
        name="Base",
        artifact_kinds=artifact_kinds,
        source_file="part_definitions.sysml",
        items={
            "attributes": {"remove_attr": 1, "replace_attr": 2, "base_only": "B"},
            "ports": {"in_a": "SignalA", "out_b": "SignalB"},
        },
    )
    intermediate = DeclaredDefinition(
        name="Intermediate",
        artifact_kinds=artifact_kinds,
        specializes="Base",
        source_file="part_definitions.sysml",
        redefines_items={"attributes": {"replace_attr": 10}, "ports": {"out_b": "SignalC"}},
        items={"attributes": {"mid_attr": 42}, "ports": {"mid_out": "SignalM"}},
    )
    derived = DeclaredDefinition(
        name="Derived",
        artifact_kinds=artifact_kinds,
        specializes="Intermediate",
        source_file="composition.sysml",
        remove_items={"attributes": {"remove_attr"}, "ports": {"in_a"}},
        redefines_items={"attributes": {"replace_attr": 99}, "ports": {"mid_out": "SignalD"}},
        items={"attributes": {"add_attr": True}, "ports": {"extra": "SignalX"}},
    )

    model = {base.name: base, intermediate.name: intermediate, derived.name: derived}
    resolved_intermediate = resolve_part(intermediate, model, cache={})
    resolved = resolve_part(derived, model, cache={})
    emitter = SysMLEmitter()

    print("Declared Intermediate:", intermediate)
    print("Declared:", derived)
    print("Resolved Intermediate:", resolved_intermediate)
    print("Resolved:", resolved)
    print("\n--- Declared Export ---")
    print(emitter.emit_declared_package("Example", model))
    print("--- Flattened Export ---")
    print(emitter.emit_flattened_package("Example", model))
    print("--- Declared Multi-file Export ---")
    for file_name, text in emitter.emit_declared_files("Example", model).items():
        print(f"# File: {file_name}")
        print(text)


if __name__ == "__main__":
    demo()
