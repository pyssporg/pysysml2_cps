from pathlib import Path

from pycps_sysmlv2 import load_architecture


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    architecture = load_architecture(repo_root / "tests" / "fixtures" / "fixture_a")
    fixture = architecture.part_definitions["FixtureAComposition"]
    print(f"package={architecture.package}")
    print(f"parts={len(architecture.part_definitions)}")
    print(f"connections={len(fixture.connections)}")
    print("subparts:")
    for subpart in fixture.parts.values():
        target_name = subpart.part_def.name if subpart.part_def else "<unresolved>"
        print(f"  - {subpart.name}: {target_name}")

    print("connections:")
    for connection in fixture.connections:
        src_part = connection.src_part_def.name if connection.src_part_def else "<unresolved>"
        dst_part = connection.dst_part_def.name if connection.dst_part_def else "<unresolved>"
        src_port = connection.src_port_def.name if connection.src_port_def else "<unresolved>"
        dst_port = connection.dst_port_def.name if connection.dst_port_def else "<unresolved>"
        print(f"  - {src_part}.{src_port} -> {dst_part}.{dst_port}")


if __name__ == "__main__":
    main()
