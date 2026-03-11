from pathlib import Path

from pycps_sysmlv2 import NodeType, SysMLParser

from public_api_test_utils import write_model, write_reference


def test_port_reference_links_to_port_definition(tmp_path: Path):
    write_model(
        tmp_path / "model.sysml",
        """
        package Example {
          port def Signal {}

          part def Node {
            in port input : Signal;
          }
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    node = architecture.part_definitions["Node"]
    ports = node.refs(NodeType.Port)

    assert ports["input"].type == "Signal"
    assert ports["input"].ref_node is not None
    assert ports["input"].ref_node.name == "Signal"
    write_reference("ports_port_reference_links", architecture)


def test_port_directions_are_preserved(tmp_path: Path):
    write_model(
        tmp_path / "model.sysml",
        """
        package Example {
          port def Signal {}

          part def Node {
            in port input : Signal;
            out port output : Signal;
          }
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    node = architecture.part_definitions["Node"]
    ports = node.refs(NodeType.Port)

    assert ports["input"].direction == "in"
    assert ports["output"].direction == "out"
    write_reference("ports_port_directions_preserved", architecture)


def test_connection_links_parts_and_port_definitions(tmp_path: Path):
    write_model(
        tmp_path / "model.sysml",
        """
        package Example {
          port def Signal {}

          part def Source {
            out port out_signal : Signal;
          }

          part def Sink {
            in port in_signal : Signal;
          }

          part def System {
            part src : Source;
            part dst : Sink;
            connect src.out_signal to dst.in_signal;
          }
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    connection = next(
        iter(architecture.part_definitions["System"].defs(NodeType.Connection).values())
    )

    assert (connection.src_part, connection.src_port) == ("src", "out_signal")
    assert (connection.dst_part, connection.dst_port) == ("dst", "in_signal")
    assert connection.src_part_node is not None
    assert connection.src_part_node.ref_node is not None
    assert connection.src_part_node.ref_node.name == "Source"
    assert connection.dst_part_node is not None
    assert connection.dst_part_node.ref_node is not None
    assert connection.dst_part_node.ref_node.name == "Sink"
    assert connection.src_port_node is not None
    assert connection.src_port_node.ref_node is not None
    assert connection.src_port_node.ref_node.name == "Signal"
    assert connection.dst_port_node is not None
    assert connection.dst_port_node.ref_node is not None
    assert connection.dst_port_node.ref_node.name == "Signal"
    write_reference("ports_connection_links", architecture)


def test_port_inheritance_adds_attributes_and_requirements(tmp_path: Path):
    write_model(
        tmp_path / "model.sysml",
        """
        package Example {
          requirement def ReqA { doc /* Requirement A */ }

          port def BasePort {
            attribute width = 8;
            requirement reqA : ReqA;
          }

          port def DerivedPort specializes BasePort {
            attribute gain = 2.0;
          }
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    derived = architecture.port_definitions["DerivedPort"]
    attrs = derived.defs(NodeType.Attribute)
    reqs = derived.refs(NodeType.Requirement)

    assert derived.specializes == "BasePort"
    assert "gain" in attrs
    assert "reqA" not in reqs
