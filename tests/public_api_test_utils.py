from pathlib import Path

from pycps_sysmlv2.parser_utils import json_dumps

REFERENCE_DIR = Path(__file__).resolve().parent / "fixtures" / "public_api_references"


def write_model(path: Path, content: str) -> None:
    path.write_text(content.strip() + "\n")


def write_reference(name: str, architecture) -> None:
    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    (REFERENCE_DIR / f"{name}.json").write_text(json_dumps(architecture, []))
