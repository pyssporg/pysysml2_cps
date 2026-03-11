from pathlib import Path

from pycps_sysmlv2 import SysMLParser

from public_api_test_utils import (
    assert_architecture_structure,
    write_package,
)


def test_requirements_are_collected(tmp_path: Path):
    """Verify requirement definitions and usages are collected and linked."""
    write_package(
        tmp_path / "requirements.sysml",
        """
        requirement def ParseRequirement {
          doc /* The system shall parse requirements. */
        }
        requirement def NormalizeRequirement {
          doc /*
            Multi-line requirement text should be normalized.
          */
        }

        port def Signal {
          requirement REQ_2 : NormalizeRequirement;
        }

        part def System {
          requirement REQ_1 : ParseRequirement;
          in port input : Signal;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()

    assert_architecture_structure(
        architecture,
        """
        package Example
        part System
          port in input:Signal -> Signal
          req REQ_1:ParseRequirement -> ParseRequirement
        port Signal
          req REQ_2:NormalizeRequirement -> NormalizeRequirement
        requirement NormalizeRequirement
          attr text:String='Multi-line requirement text should be normalized.'
        requirement ParseRequirement
          attr text:String='The system shall parse requirements.'
        """,
    )


def test_requirement_definition_inheritance(tmp_path: Path):
    """Verify requirement specialization links derived requirements to base definitions."""
    write_package(
        tmp_path / "requirements.sysml",
        """
        requirement def BaseReq {
          doc /* Base requirement text */
        }

        requirement def DerivedReq specializes BaseReq {}

        part def System {
          requirement REQ_1 : DerivedReq;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    assert_architecture_structure(
        architecture,
        """
        package Example
        part System
          req REQ_1:DerivedReq -> DerivedReq
        requirement BaseReq
          attr text:String='Base requirement text'
        requirement DerivedReq specializes BaseReq
        """,
    )
