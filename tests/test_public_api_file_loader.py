from pathlib import Path

from pycps_sysmlv2 import SysMLParser

from public_api_test_utils import write_model, write_reference


def test_load_architecture_from_directory(tmp_path: Path):
    write_model(
        tmp_path / "main.sysml",
        """
        package Example {
          part def Child {}
          part def System {
            part child : Child;
          }
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()

    assert architecture.package == "Example"
    assert set(architecture.part_definitions) == {"Child", "System"}
    write_reference("file_loader_load_architecture_from_directory", architecture, True)


def test_load_architecture_from_file_path(tmp_path: Path):
    model_path = tmp_path / "model.sysml"
    write_model(
        model_path,
        """
        package Example {
          part def Child {}
        }
        """,
    )

    architecture = SysMLParser(model_path).parse()

    assert architecture.package == "Example"
    assert "Child" in architecture.part_definitions
    write_reference("file_loader_load_architecture_from_file_path", architecture, True)


def test_directory_load_merges_multiple_sysml_files(tmp_path: Path):
    write_model(
        tmp_path / "ports.sysml",
        """
        package Example {
          port def Signal {}
        }
        """,
    )
    write_model(
        tmp_path / "part1.sysml",
        """
        package Example {
          part def Consumer {
            in port in_signal : Signal;
          }
        }
        """,
    )
    write_model(
        tmp_path / "part2.sysml",
        """
        package Example {
          part def Producer {
            out port out_signal : Signal;
          }
        }
        """,
    )
    write_model(
        tmp_path / "composition.sysml",
        """
        package Example {
          part def System {
            part src : Producer;
            part dst : Consumer;
            connect src.out_signal to dst.in_signal;
          }
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()

    assert set(architecture.port_definitions) == {"Signal"}
    assert set(architecture.part_definitions) == {"Consumer", "Producer", "System"}
    connection = architecture.part_definitions["System"].connections[0]
    assert connection.src_port_def is not None
    assert connection.src_port_def.name == "Signal"
    write_reference("file_loader_directory_load_merges_multiple_sysml_files", architecture, True)


def test_architecture_get_part_returns_requested_part_definition(tmp_path: Path):
    write_model(
        tmp_path / "model.sysml",
        """
        package Example {
          part def Child {}
          part def System {
            part child : Child;
          }
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    system = architecture.get_part("System")

    assert system.name == "System"
    assert "child" in system.parts
    assert system.parts["child"].part_name == "Child"
    write_reference("file_loader_get_part_returns_requested_part_definition", architecture, True)


def test_load_architecture_from_file_does_not_parse_sibling_files(tmp_path: Path):
    model_path = tmp_path / "model.sysml"
    write_model(
        model_path,
        """
        package Example {
          part def Child {}
        }
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

    assert architecture.package == "Example"
    assert set(architecture.part_definitions) == {"Child"}
    write_reference("file_loader_file_does_not_parse_siblings", architecture)
