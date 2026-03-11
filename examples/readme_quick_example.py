from __future__ import annotations

from pycps_sysmlv2 import NodeType

from examples._example_helpers import parse_demo_architecture


def main() -> None:
    architecture = parse_demo_architecture()
    system = architecture.part_definitions["System"]

    connections = list(system.defs(NodeType.Connection).values())
    assert len(connections) == 1

    connection = connections[0]
    print(connection.src_part, "->", connection.dst_part)


if __name__ == "__main__":
    main()
