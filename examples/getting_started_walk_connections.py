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
        connection = next(iter(system.defs(NodeType.Connection).values()))

        assert connection.src_part == "src"
        assert connection.src_port == "out_signal"
        assert connection.dst_part == "dst"
        assert connection.dst_port == "in_signal"


if __name__ == "__main__":
    main()
