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
        subparts = system.refs(NodeType.Part)

        assert subparts["src"].type == "Source"
        assert subparts["src"].ref_node.name == "Source"
        assert subparts["dst"].type == "Sink"
        assert subparts["dst"].ref_node.name == "Sink"

        source = architecture.part_definitions["Source"]
        port_ref = source.refs(NodeType.Port)["out_signal"]
        assert port_ref.direction == "out"
        assert port_ref.ref_node.name == "Signal"


if __name__ == "__main__":
    main()
