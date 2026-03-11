from __future__ import annotations

from examples._example_helpers import parse_demo_architecture


def main() -> None:
    architecture = parse_demo_architecture()

    declared_files = architecture.export_declared()
    flattened_text = architecture.export_flattened()

    assert set(declared_files) == {"model.sysml"}
    assert "requirement def ReqA" in declared_files["model.sysml"]
    assert "part def System {" in flattened_text


if __name__ == "__main__":
    main()
