from pathlib import Path

from pycps_sysmlv2 import export_architecture, export_architecture_files
from pycps_sysmlv2.parser_utils import json_dumps

REFERENCE_DIR = Path(__file__).resolve().parent / "public_api_references"


def write_model(path: Path, content: str) -> None:
    path.write_text(content.strip() + "\n")


def write_reference(name: str, architecture, export_files=False) -> None:
    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    (REFERENCE_DIR / f"{name}.json").write_text(json_dumps(architecture, []))
    if export_files:
        for i, item in export_architecture_files(architecture).items():
            (REFERENCE_DIR / f"{name}_{i}.sysml").write_text(item)
