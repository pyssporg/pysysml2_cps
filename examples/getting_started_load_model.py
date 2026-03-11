from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from pycps_sysmlv2 import SysMLParser

from examples._example_helpers import write_demo_model


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        model_path = write_demo_model(root)

        architecture_from_file = SysMLParser(model_path).parse()
        architecture_from_directory = SysMLParser(root).parse()

        assert architecture_from_file.package == "Example"
        assert architecture_from_directory.package == "Example"


if __name__ == "__main__":
    main()
