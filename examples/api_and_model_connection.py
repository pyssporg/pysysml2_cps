from __future__ import annotations

from pycps_sysmlv2 import NodeType

from examples._example_helpers import parse_demo_architecture


def main() -> None:
    architecture = parse_demo_architecture()
    system = architecture.part_definitions["System"]
    connections = system.defs(NodeType.Connection)
    assert list(connections) == ["src.out_signal->dst.in_signal"]


if __name__ == "__main__":
    main()
