from pathlib import Path

from pycps_sysmlv2 import load_architecture

from public_api_test_utils import write_model, write_reference


def test_requirements_are_collected(tmp_path: Path):
    write_model(
        tmp_path / "requirements.sysml",
        """
        package Example {
          comment REQ_1 /* The system shall parse requirements. */
          comment REQ_2 /*
            Multi-line requirement text should be normalized.
          */
        }
        """,
    )

    architecture = load_architecture(tmp_path)

    assert [req.identifier for req in architecture.requirements] == ["REQ_1", "REQ_2"]
    assert architecture.requirements[0].text == "The system shall parse requirements."
    assert architecture.requirements[1].text == (
        "Multi-line requirement text should be normalized."
    )
    write_reference("requirements_collected", architecture)
