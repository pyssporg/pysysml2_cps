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

        declared_files = architecture.export_declared()
        flattened_text = architecture.export_flattened()

        assert set(declared_files) == {"model.sysml"}
        assert "part def System {" in declared_files["model.sysml"]
        assert "package Example {" in flattened_text


if __name__ == "__main__":
    main()
