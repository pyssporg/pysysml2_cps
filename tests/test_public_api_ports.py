from pathlib import Path

from pycps_sysmlv2 import load_architecture

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

    architecture = load_architecture(tmp_path)
    node = architecture.part_definitions["Node"]

    assert node.ports["input"].port_name == "Signal"
    assert node.ports["input"].port_def is not None
    assert node.ports["input"].port_def.name == "Signal"
    write_reference("ports_port_reference_links", architecture)


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

    architecture = load_architecture(tmp_path)
    connection = architecture.part_definitions["System"].connections[0]

    assert (connection.src_component, connection.src_port) == ("src", "out_signal")
    assert (connection.dst_component, connection.dst_port) == ("dst", "in_signal")
    assert connection.src_part_def is not None
    assert connection.src_part_def.name == "Source"
    assert connection.dst_part_def is not None
    assert connection.dst_part_def.name == "Sink"
    assert connection.src_port_def is not None
    assert connection.src_port_def.name == "Signal"
    assert connection.dst_port_def is not None
    assert connection.dst_port_def.name == "Signal"
    write_reference("ports_connection_links", architecture)
