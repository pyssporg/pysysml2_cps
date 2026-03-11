from pathlib import Path

from pycps_sysmlv2 import SysMLParser

from public_api_test_utils import (
    assert_architecture_structure,
    write_model,
    write_package,
)


def test_load_architecture_from_directory(tmp_path: Path):
    """Verify parsing a directory loads and merges all .sysml files in that directory."""
    write_package(
        tmp_path / "main.sysml",
        """
        part def Child {}
        part def System {
          part child : Child;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()

    assert_architecture_structure(
        architecture,
        """
        package Example
        part Child
        part System
          part child:Child -> Child
        """,
    )


def test_load_architecture_from_file_path(tmp_path: Path):
    """Verify parsing a single file path loads only that file."""
    model_path = tmp_path / "model.sysml"
    write_package(
        model_path,
        """
        part def Child {}
        """,
    )

    architecture = SysMLParser(model_path).parse()

    assert_architecture_structure(
        architecture,
        """
        package Example
        part Child
        """,
    )


def test_directory_load_merges_multiple_sysml_files(tmp_path: Path):
    """Verify multi-file models resolve cross-file references and connections."""
    write_package(
        tmp_path / "ports.sysml",
        """
        port def Signal {}
        """,
    )
    write_package(
        tmp_path / "part1.sysml",
        """
        part def Consumer {
          in port in_signal : Signal;
        }
        """,
    )
    write_package(
        tmp_path / "part2.sysml",
        """
        part def Producer {
          out port out_signal : Signal;
        }
        """,
    )
    write_package(
        tmp_path / "composition.sysml",
        """
        part def System {
          part src : Producer;
          part dst : Consumer;
          connect src.out_signal to dst.in_signal;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()

    assert_architecture_structure(
        architecture,
        """
        package Example
        part Consumer
          port in in_signal:Signal -> Signal
        part Producer
          port out out_signal:Signal -> Signal
        part System
          part dst:Consumer -> Consumer
          part src:Producer -> Producer
          connect src.out_signal -> dst.in_signal
        port Signal
        """,
    )


def test_architecture_get_part_returns_requested_part_definition(tmp_path: Path):
    """Verify named part definitions are retrievable from the parsed package registry."""
    write_package(
        tmp_path / "model.sysml",
        """
        part def Child {}
        part def System {
          part child : Child;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    assert_architecture_structure(
        architecture,
        """
        package Example
        part Child
        part System
          part child:Child -> Child
        """,
    )


def test_load_architecture_from_file_does_not_parse_sibling_files(tmp_path: Path):
    """Verify parsing one file ignores sibling files in the same directory."""
    model_path = tmp_path / "model.sysml"
    write_package(
        model_path,
        """
        part def Child {}
        """,
    )
    write_model(
        tmp_path / "other.sysml",
        """
        package WrongPackage {
          part def ShouldNotBeLoaded {}
        }
        """,
    )

    architecture = SysMLParser(model_path).parse()

    assert_architecture_structure(
        architecture,
        """
        package Example
        part Child
        """,
    )
