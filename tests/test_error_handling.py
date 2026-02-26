from pathlib import Path

import pytest

from pycps_sysmlv2 import load_architecture, load_system


def _write(path: Path, content: str) -> None:
    path.write_text(content.strip() + "\n")


def test_load_system_raises_key_error_for_missing_part(tmp_path: Path):
    _write(
        tmp_path / "model.sysml",
        """
        package Example {
          part def Present {}
        }
        """,
    )

    with pytest.raises(KeyError, match="Part not found: Missing"):
        load_system(tmp_path, "Missing")


def test_missing_port_definition_fails_with_context(tmp_path: Path):
    _write(
        tmp_path / "model.sysml",
        """
        package Example {
          part def A {
            out port x : MissingPortType;
          }
        }
        """,
    )

    with pytest.raises(ValueError, match="Port definition not found for A.x"):
        load_architecture(tmp_path)


def test_connection_to_unknown_part_definition_fails_with_context(tmp_path: Path):
    _write(
        tmp_path / "model.sysml",
        """
        package Example {
          port def Signal {}

          part def KnownPart {
            out port out_signal : Signal;
          }

          part def System {
            part known : KnownPart;
            part unknown : UnknownPart;
            connect known.out_signal to unknown.in_signal;
          }
        }
        """,
    )

    with pytest.raises(
        ValueError, match="Part definition not found for subpart System.unknown"
    ):
        load_architecture(tmp_path)


def test_part_inheritance_unknown_base_fails(tmp_path: Path):
    _write(
        tmp_path / "model.sysml",
        """
        package Example {
          part def Derived : MissingBase {
            attribute x = 1;
          }
        }
        """,
    )

    with pytest.raises(
        ValueError, match="Base part definition not found for Derived: MissingBase"
    ):
        load_architecture(tmp_path)


def test_part_inheritance_cycle_fails(tmp_path: Path):
    _write(
        tmp_path / "model.sysml",
        """
        package Example {
          part def A : B {}
          part def B : C {}
          part def C : A {}
        }
        """,
    )

    with pytest.raises(ValueError, match="Inheritance cycle detected"):
        load_architecture(tmp_path)


def test_replace_requires_existing_member(tmp_path: Path):
    _write(
        tmp_path / "model.sysml",
        """
        package Example {
          part def Base {
            attribute present = 1;
          }
          part def Derived : Base {
            replace attribute missing = 2;
          }
        }
        """,
    )

    with pytest.raises(ValueError, match="Cannot replace unknown attribute Derived.missing"):
        load_architecture(tmp_path)


def test_remove_requires_existing_member(tmp_path: Path):
    _write(
        tmp_path / "model.sysml",
        """
        package Example {
          part def Base {}
          part def Derived : Base {
            remove port missingPort;
          }
        }
        """,
    )

    with pytest.raises(ValueError, match="Cannot remove unknown port Derived.missingPort"):
        load_architecture(tmp_path)


def test_add_collision_requires_replace(tmp_path: Path):
    _write(
        tmp_path / "model.sysml",
        """
        package Example {
          part def Base {
            attribute value = 1;
          }
          part def Derived : Base {
            attribute value = 2;
          }
        }
        """,
    )

    with pytest.raises(
        ValueError,
        match="Attribute name collision in Derived: value \\(use replace attribute\\)",
    ):
        load_architecture(tmp_path)


def test_replace_connect_is_not_supported(tmp_path: Path):
    _write(
        tmp_path / "model.sysml",
        """
        package Example {
          part def Base {
            part a : Base;
            part b : Base;
            connect a.p to b.p;
          }
          part def Derived : Base {
            replace connect a.p to b.p;
          }
        }
        """,
    )

    with pytest.raises(ValueError, match="Malformed replace statement"):
        load_architecture(tmp_path)
