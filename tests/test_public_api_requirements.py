from pathlib import Path

from pycps_sysmlv2 import load_architecture

from public_api_test_utils import write_model, write_reference


def test_requirements_are_collected(tmp_path: Path):
    write_model(
        tmp_path / "requirements.sysml",
        """
        package Example {
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
        }
        """,
    )

    architecture = load_architecture(tmp_path)

    assert set(architecture.requirement_definitions) == {
        "NormalizeRequirement",
        "ParseRequirement",
    }
    system_reqs = architecture.part_definitions["System"].items["requirements"]
    signal_reqs = architecture.port_definitions["Signal"].items["requirements"]
    assert [req.identifier for req in system_reqs.values()] == ["REQ_1"]
    assert [req.identifier for req in signal_reqs.values()] == ["REQ_2"]
    assert next(iter(system_reqs.values())).text == "The system shall parse requirements."
    assert next(iter(signal_reqs.values())).text == (
        "Multi-line requirement text should be normalized."
    )
    write_reference("requirements_collected", architecture)


def test_requirement_definition_inheritance(tmp_path: Path):
    write_model(
        tmp_path / "requirements.sysml",
        """
        package Example {
          requirement def BaseReq {
            doc /* Base requirement text */
          }

          requirement def DerivedReq specializes BaseReq {}

          part def System {
            requirement REQ_1 : DerivedReq;
          }
        }
        """,
    )

    architecture = load_architecture(tmp_path)
    derived = architecture.requirement_definitions["DerivedReq"]
    req_ref = architecture.part_definitions["System"].items["requirements"]["REQ_1"]

    assert derived.specializes == "BaseReq"
    assert derived.text == "Base requirement text"
    assert req_ref.requirement_def is not None
    assert req_ref.requirement_def.name == "DerivedReq"
    assert req_ref.text == "Base requirement text"
