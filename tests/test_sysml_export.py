from pathlib import Path

from pycps_sysmlv2 import SysMLParser

from public_api_test_utils import write_model


def test_export_declared_and_flattened_sysml(tmp_path: Path):
    write_model(
        tmp_path / "model.sysml",
        """
        package Example {
          requirement def ReqA {
            doc /* Requirement A */
          }

          port def SignalA {}
          port def SignalB {}

          part def Base {
            attribute keep = 1;
            attribute replace_me = 2;
            out port out_a : SignalA;
            requirement keep_req : ReqA;
          }

          part def Derived specializes Base {
            redefines attribute replace_me = 99;
            out port out_b : SignalB;
          }
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    declared = architecture.export_declared()["model.sysml"]
    flattened = architecture.export_flattened()

    assert "part def Derived specializes Base" in declared
    assert "redefines attribute replace_me = 99;" in declared
    assert "requirement def ReqA {" in declared
    derived_block = flattened.split("part def Derived {", 1)[1]
    assert "requirement keep_req : ReqA;" not in derived_block
    assert "part def Derived {" in flattened
    assert "specializes Base" not in flattened
    assert "attribute keep = 1;" not in derived_block
    assert "attribute replace_me = 99;" in derived_block


def test_export_declared_preserves_source_grouping(tmp_path: Path):
    write_model(
        tmp_path / "part_definitions.sysml",
        """
        package Example {
          port def Signal {}

          part def Base {
            attribute a = 1;
            out port out_a : Signal;
          }
        }
        """,
    )
    write_model(
        tmp_path / "composition.sysml",
        """
        package Example {
          part def Derived specializes Base {
            redefines attribute a = 2;
          }
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    files = architecture.export_declared()

    assert set(files) == {"composition.sysml", "part_definitions.sysml"}
    assert "part def Derived specializes Base" in files["composition.sysml"]
    assert "part def Base {" in files["part_definitions.sysml"]


def test_export_declared_includes_port_only_source_files(tmp_path: Path):
    write_model(
        tmp_path / "ports.sysml",
        """
        package Example {
          port def Signal {}
        }
        """,
    )
    write_model(
        tmp_path / "parts.sysml",
        """
        package Example {
          part def Node {
            in port input : Signal;
          }
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    files = architecture.export_declared()

    assert set(files) == {"parts.sysml", "ports.sysml"}
    assert "port def Signal {" in files["ports.sysml"]
    assert "part def Node {" in files["parts.sysml"]
