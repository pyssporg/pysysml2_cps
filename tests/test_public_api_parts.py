from pathlib import Path

from pycps_sysmlv2 import NodeType, SysMLParser
from pycps_sysmlv2.definitions import PrimitiveType, SysMLType

from public_api_test_utils import write_package, write_reference


def test_attribute_literals_are_parsed(tmp_path: Path):
    """Verify literal-valued attributes are parsed with inferred types."""
    write_package(
        tmp_path / "model.sysml",
        """
        part def Node {
          attribute values = [1.0, 2.0, 3.0];
          attribute count = 3;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    node = architecture.part_definitions["Node"]
    attrs = node.defs(NodeType.Attribute)
    values = attrs["values"]

    assert values.value == [1.0, 2.0, 3.0]
    assert isinstance(values.type, SysMLType)
    assert values.type.primitive_type() == PrimitiveType.Real
    assert attrs["count"].value == 3
    write_reference("parts_attribute_literals_parsed", architecture)


def test_typed_attributes_without_values_are_parsed(tmp_path: Path):
    """Verify typed attributes without literals retain type and null value."""
    write_package(
        tmp_path / "model.sysml",
        """
        part def Node {
          attribute gain : float64;
          attribute enabled : boolean;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    node = architecture.part_definitions["Node"]
    attrs = node.defs(NodeType.Attribute)

    assert attrs["gain"].value is None
    assert isinstance(attrs["gain"].type, SysMLType)
    assert attrs["gain"].type.primitive_type() == PrimitiveType.Real
    assert attrs["enabled"].value is None
    assert isinstance(attrs["enabled"].type, SysMLType)
    assert attrs["enabled"].type.primitive_type() == PrimitiveType.Boolean
    write_reference("parts_typed_attributes_without_values", architecture)


def test_subpart_reference_links_to_part_definition(tmp_path: Path):
    """Verify subpart usages resolve to their part definition nodes."""
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
    system = architecture.part_definitions["System"]
    parts = system.refs(NodeType.Part)

    assert parts["child"].type == "Child"
    assert parts["child"].ref_node is not None
    assert parts["child"].ref_node.name == "Child"
    write_reference("parts_subpart_reference_links", architecture)


def test_doc_comments_are_attached_to_definitions(tmp_path: Path):
    """Verify doc comments attach to the intended definitions and members."""
    write_package(
        tmp_path / "model.sysml",
        """
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
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    signal = architecture.port_definitions["Signal"]
    node = architecture.part_definitions["Node"]
    signal_attrs = signal.defs(NodeType.Attribute)
    node_attrs = node.defs(NodeType.Attribute)
    node_ports = node.refs(NodeType.Port)

    assert signal.doc == "signal docs"
    assert signal_attrs["p"].doc == "payload docs"
    assert node.doc == "node docs"
    assert node_attrs["threshold"].doc == "attribute docs"
    assert node_ports["input"].doc == "input docs"
    write_reference("parts_doc_comments_attached_to_definitions", architecture)
