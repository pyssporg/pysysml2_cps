from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from pycps_sysmlv2 import NodeType, SysMLParser

from examples._example_helpers import write_demo_model


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_demo_model(root)
        architecture = SysMLParser(root).parse()

        system = architecture.part_definitions["System"]

        attributes = system.defs(NodeType.Attribute)
        subparts = system.refs(NodeType.Part)
        ports = system.refs(NodeType.Port)
        requirements = system.refs(NodeType.Requirement)
        connections = system.defs(NodeType.Connection)

        assert attributes == {}
        assert sorted(subparts) == ["dst", "src"]
        assert ports == {}
        assert list(requirements) == ["system_req"]
        assert list(connections) == ["src.out_signal->dst.in_signal"]


if __name__ == "__main__":
    main()
