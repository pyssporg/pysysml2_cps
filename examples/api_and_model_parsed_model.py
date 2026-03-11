from __future__ import annotations

from pycps_sysmlv2 import NodeType

from examples._example_helpers import parse_demo_architecture


def main() -> None:
    architecture = parse_demo_architecture()

    assert architecture.package == "Example"
    assert sorted(architecture.defs(NodeType.Part)) == ["Sink", "Source", "System"]
    assert list(architecture.defs(NodeType.Port)) == ["Signal"]
    assert list(architecture.defs(NodeType.Requirement)) == ["ReqA"]


if __name__ == "__main__":
    main()
