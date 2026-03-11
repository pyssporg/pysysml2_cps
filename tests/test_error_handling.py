from pathlib import Path

import pytest

from pycps_sysmlv2 import NodeType, SysMLParser
from public_api_test_utils import write_package


def _write_example(path: Path, body: str) -> None:
    write_package(path, body, package_name="Example")


def test_get_part_raises_key_error_for_missing_part(tmp_path: Path):
    """Verify missing part lookups raise KeyError from the part registry."""
    _write_example(
        tmp_path / "model.sysml",
        """

        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    with pytest.raises(KeyError, match="Missing"):
        _ = architecture.part_definitions["Missing"]


def test_missing_port_definition_fails_with_context(tmp_path: Path):
    """Verify unresolved port types produce contextual validation errors."""
    _write_example(
        tmp_path / "model.sysml",
        """
        part def A {
          out port x : MissingPortType;
        }
        """,
    )

    with pytest.raises(ValueError, match="Port definition not found for A.x"):
        SysMLParser(tmp_path).parse()


def test_connection_to_unknown_part_definition_fails_with_context(tmp_path: Path):
    """Verify connections fail when a referenced subpart type cannot be resolved."""
    _write_example(
        tmp_path / "model.sysml",
        """
        part def KnownPart {}

        part def System {
          part known : KnownPart;
          part unknown : UnknownPart;
          connect known.out_signal to unknown.in_signal;
        }
        """,
    )

    with pytest.raises(
        ValueError, match="Part definition not found for subpart System.unknown"
    ):
        SysMLParser(tmp_path).parse()


def test_part_inheritance_unknown_base_fails(tmp_path: Path):
    """Verify specialization fails when a base part definition is missing."""
    _write_example(
        tmp_path / "model.sysml",
        """
        part def Derived specializes MissingBase {
          attribute x = 1;
        }
        """,
    )

    with pytest.raises(
        ValueError, match="Base part definition not found for Derived: MissingBase"
    ):
        SysMLParser(tmp_path).parse()


def test_legacy_colon_inheritance_syntax_is_rejected(tmp_path: Path):
    """Verify deprecated colon-based inheritance syntax is rejected."""
    _write_example(
        tmp_path / "model.sysml",
        """
        part def Derived : Base {}
        """,
    )

    with pytest.raises(
        ValueError, match="Legacy inheritance syntax ':' is not supported"
    ):
        SysMLParser(tmp_path).parse()


def test_part_inheritance_cycle_fails(tmp_path: Path):
    """Verify cyclic part specialization graphs are rejected."""
    _write_example(
        tmp_path / "model.sysml",
        """
        part def A specializes B {}
        part def B specializes C {}
        part def C specializes A {}
        """,
    )

    with pytest.raises(ValueError, match="Inheritance cycle detected"):
        SysMLParser(tmp_path).parse()


def test_redefines_on_missing_member_is_accepted_as_override(tmp_path: Path):
    """Verify redefining a non-existent inherited member acts as an effective override."""
    _write_example(
        tmp_path / "model.sysml",
        """
        part def Base {}
        part def Derived specializes Base {
          redefines attribute missing = 2;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    derived = architecture.part_definitions["Derived"]
    assert derived.defs(NodeType.Attribute)["missing"].value == 2


def test_remove_missing_member_is_noop(tmp_path: Path):
    """Verify removing a missing member is treated as a no-op."""
    _write_example(
        tmp_path / "model.sysml",
        """
        part def Base {}
        part def Derived specializes Base {
          remove port missingPort;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    assert architecture.part_definitions["Derived"].refs(NodeType.Port) == {}


def test_add_collision_in_derived_is_allowed(tmp_path: Path):
    """Verify derived declarations can shadow base members under current semantics."""
    _write_example(
        tmp_path / "model.sysml",
        """
        part def Base {
          attribute value = 1;
        }
        part def Derived specializes Base {
          attribute value = 2;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    assert architecture.part_definitions["Derived"].defs(NodeType.Attribute)["value"].value == 2


def test_replace_syntax_is_rejected(tmp_path: Path):
    """Verify unsupported replace statements are reported as unknown syntax."""
    _write_example(
        tmp_path / "model.sysml",
        """
        part def Base {}
        part def Derived specializes Base {
          replace connect a.p to b.p;
        }
        """,
    )

    with pytest.raises(
        ValueError,
        match="Unknown statement while parsing part def Derived in package Example",
    ):
        SysMLParser(tmp_path).parse()


def test_comment_based_requirements_are_rejected(tmp_path: Path):
    """Verify legacy comment-style requirement declarations are rejected."""
    _write_example(
        tmp_path / "model.sysml",
        """
        comment REQ_1 /* legacy style requirement */
        """,
    )

    with pytest.raises(
        ValueError,
        match="Comment-based requirements are not supported; use requirement def/requirement syntax",
    ):
        SysMLParser(tmp_path).parse()


def test_requirement_usage_requires_known_definition(tmp_path: Path):
    """Verify requirement usages must reference an existing requirement definition."""
    _write_example(
        tmp_path / "model.sysml",
        """
        part def System {
          requirement MissingReq : MissingDef;
        }
        """,
    )

    with pytest.raises(
        ValueError, match="Requirement usage references unknown requirement definition"
    ):
        SysMLParser(tmp_path).parse()


def test_top_level_requirement_usage_is_rejected(tmp_path: Path):
    """Verify requirement usages are only allowed inside part/port definition blocks."""
    _write_example(
        tmp_path / "model.sysml",
        """
        requirement def ReqA { doc /* req */ }
        requirement REQ_1 : ReqA;
        """,
    )

    with pytest.raises(
        ValueError, match="Requirement usage must be declared inside part def or port def blocks"
    ):
        SysMLParser(tmp_path).parse()


def test_unknown_part_statement_fails_with_context(tmp_path: Path):
    """Verify unknown statements inside part definitions surface contextual errors."""
    _write_example(
        tmp_path / "model.sysml",
        """
        part def Node {
          action unsupported();
        }
        """,
    )

    with pytest.raises(
        ValueError,
        match="Unknown statement while parsing part def Node in package Example",
    ):
        SysMLParser(tmp_path).parse()
