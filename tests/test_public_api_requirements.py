from pathlib import Path

from pycps_sysmlv2 import NodeType, SysMLParser

from public_api_test_utils import write_package, write_reference


def test_requirements_are_collected(tmp_path: Path):
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

    assert set(architecture.requirement_definitions) == {
        "NormalizeRequirement",
        "ParseRequirement",
    }
    system_reqs = architecture.part_definitions["System"].refs(NodeType.Requirement)
    signal_reqs = architecture.port_definitions["Signal"].refs(NodeType.Requirement)
    assert [req.name for req in system_reqs.values()] == ["REQ_1"]
    assert [req.name for req in signal_reqs.values()] == ["REQ_2"]
    assert next(iter(system_reqs.values())).ref_node.text == "The system shall parse requirements."
    assert next(iter(signal_reqs.values())).ref_node.text == (
        "Multi-line requirement text should be normalized."
    )
    write_reference("requirements_collected", architecture)


def test_requirement_definition_inheritance(tmp_path: Path):
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
    derived = architecture.requirement_definitions["DerivedReq"]
    req_ref = architecture.part_definitions["System"].refs(NodeType.Requirement)["REQ_1"]

    assert derived.specializes == "BaseReq"
    assert derived.specializes_obj is not None
    assert derived.specializes_obj.text == "Base requirement text"
    assert req_ref.ref_node is not None
    assert req_ref.ref_node.name == "DerivedReq"
