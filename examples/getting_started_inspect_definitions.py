from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from pycps_sysmlv2 import SysMLParser

from examples._example_helpers import write_demo_model


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_demo_model(root)
        architecture = SysMLParser(root).parse()

        system = architecture.part_definitions["System"]
        signal = architecture.port_definitions["Signal"]
        requirement = architecture.requirement_definitions["ReqA"]

        assert system.name == "System"
        assert signal.name == "Signal"
        assert requirement.text == "Example requirement"


if __name__ == "__main__":
    main()
