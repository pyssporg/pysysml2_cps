from pathlib import Path

import pytest

from pycps_sysmlv2 import SysMLParser

from public_api_test_utils import write_model, write_package


def test_parse_missing_path_raises_file_not_found(tmp_path: Path):
    """Verify parsing a missing file or directory reports FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="No .sysml file found under"):
        SysMLParser(tmp_path / "missing.sysml").parse()


def test_parse_empty_directory_raises_file_not_found(tmp_path: Path):
    """Verify parsing an empty directory reports the missing SysML file set."""
    with pytest.raises(FileNotFoundError, match="No .sysml files found under"):
        SysMLParser(tmp_path).parse()


def test_missing_package_declaration_fails(tmp_path: Path):
    """Verify top-level input without a package block is rejected."""
    write_model(
        tmp_path / "model.sysml",
        """
        part def Node {}
        """,
    )

    with pytest.raises(ValueError, match="No package declaration found"):
        SysMLParser(tmp_path).parse()


def test_mismatched_package_names_across_files_fail(tmp_path: Path):
    """Verify directory parsing rejects mixed package names."""
    write_package(tmp_path / "a.sysml", "part def A {}", package_name="PkgA")
    write_package(tmp_path / "b.sysml", "part def B {}", package_name="PkgB")

    with pytest.raises(ValueError, match="Mismatched package names: PkgA vs PkgB"):
        SysMLParser(tmp_path).parse()


def test_duplicate_part_definitions_across_files_fail(tmp_path: Path):
    """Verify duplicate part names are rejected during directory load."""
    write_package(tmp_path / "a.sysml", "part def Node {}")
    write_package(tmp_path / "b.sysml", "part def Node {}")

    with pytest.raises(ValueError, match="Duplicate part definition for Node"):
        SysMLParser(tmp_path).parse()


def test_duplicate_port_definitions_across_files_fail(tmp_path: Path):
    """Verify duplicate port names are rejected during directory load."""
    write_package(tmp_path / "a.sysml", "port def Signal {}")
    write_package(tmp_path / "b.sysml", "port def Signal {}")

    with pytest.raises(ValueError, match="Duplicate port definition for Signal"):
        SysMLParser(tmp_path).parse()


def test_duplicate_requirement_definitions_across_files_fail(tmp_path: Path):
    """Verify duplicate requirement names are rejected during directory load."""
    write_package(tmp_path / "a.sysml", "requirement def ReqA {}")
    write_package(tmp_path / "b.sysml", "requirement def ReqA {}")

    with pytest.raises(ValueError, match="Duplicate requirement definition for ReqA"):
        SysMLParser(tmp_path).parse()
