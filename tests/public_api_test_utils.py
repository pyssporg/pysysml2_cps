from copy import deepcopy
from pathlib import Path
from textwrap import dedent

from pycps_sysmlv2 import architecture_structure


def write_model(path: Path, content: str) -> None:
    path.write_text(content.strip() + "\n")


def write_package(path: Path, body: str, package_name: str = "Example") -> None:
    normalized_body = dedent(body).strip()
    write_model(
        path,
        f"""
        package {package_name} {{
        {normalized_body}
        }}
        """,
    )


def assert_architecture_structure(architecture, expected: str) -> None:
    expected_norm = dedent(expected).strip() + "\n"
    assert architecture_structure(architecture) == expected_norm
