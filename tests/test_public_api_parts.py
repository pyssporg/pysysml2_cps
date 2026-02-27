from pathlib import Path

from pycps_sysmlv2 import load_architecture
from pycps_sysmlv2.definitions import PrimitiveType, SysMLType

from public_api_test_utils import write_model, write_reference
def test_attribute_literals_are_parsed(tmp_path: Path):
    write_model(
        tmp_path / "model.sysml",
        """
        package Example {
          part def Node {
            attribute values = [1.0, 2.0, 3.0];
            attribute count = 3;
          }
        }
        """,
    )

    architecture = load_architecture(tmp_path)
    node = architecture.part_definitions["Node"]
    values = node.attributes["values"]

    assert values.value == [1.0, 2.0, 3.0]
    assert isinstance(values.type, SysMLType)
    assert values.type.primitive_type() == PrimitiveType.Real
    assert node.attributes["count"].value == 3
    write_reference("parts_attribute_literals_parsed", architecture)


def test_subpart_reference_links_to_part_definition(tmp_path: Path):
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

    architecture = load_architecture(tmp_path)
    system = architecture.part_definitions["System"]

    assert system.parts["child"].part_name == "Child"
    assert system.parts["child"].part_def is not None
    assert system.parts["child"].part_def.name == "Child"
    write_reference("parts_subpart_reference_links", architecture)


def test_doc_comments_are_attached_to_definitions(tmp_path: Path):
    write_model(
        tmp_path / "model.sysml",
        """
        package Example {
          port def Signal {
            doc /* signal docs */
            doc /* payload docs */
            attribute p = 1;
          }

          part def Node {
            doc /* node docs */
            doc /* attribute docs */
            attribute threshold = 2;
            doc /* input docs */
            in port input : Signal;
          }
        }
        """,
    )

    architecture = load_architecture(tmp_path)
    signal = architecture.port_definitions["Signal"]
    node = architecture.part_definitions["Node"]

    assert signal.doc == "signal docs"
    assert signal.attributes["p"].doc == "payload docs"
    assert node.doc == "node docs"
    assert node.attributes["threshold"].doc == "attribute docs"
    assert node.ports["input"].doc == "input docs"
    write_reference("parts_doc_comments_attached_to_definitions", architecture)
