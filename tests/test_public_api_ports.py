from pathlib import Path

from pycps_sysmlv2 import SysMLParser

from public_api_test_utils import (
    assert_architecture_structure,
    write_package,
)


def test_port_reference_links_to_port_definition(tmp_path: Path):
    """Verify part port usages link to their referenced port definitions."""
    write_package(
        tmp_path / "model.sysml",
        """
        port def Signal {}

        part def Node {
          in port input : Signal;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    assert_architecture_structure(
        architecture,
        """
        package Example
        part Node
          port in input:Signal -> Signal
        port Signal
        """,
    )


def test_port_directions_are_preserved(tmp_path: Path):
    """Verify parser preserves in/out direction on port usages."""
    write_package(
        tmp_path / "model.sysml",
        """
        port def Signal {}

        part def Node {
          in port input : Signal;
          out port output : Signal;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    assert_architecture_structure(
        architecture,
        """
        package Example
        part Node
          port in input:Signal -> Signal
          port out output:Signal -> Signal
        port Signal
        """,
    )


def test_connection_links_parts_and_port_definitions(tmp_path: Path):
    """Verify connections resolve to both part usages and port definitions."""
    write_package(
        tmp_path / "model.sysml",
        """
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
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    assert_architecture_structure(
        architecture,
        """
        package Example
        part Sink
          port in in_signal:Signal -> Signal
        part Source
          port out out_signal:Signal -> Signal
        part System
          part dst:Sink -> Sink
          part src:Source -> Source
          connect src.out_signal -> dst.in_signal
        port Signal
        """,
    )


def test_port_inheritance_adds_attributes_and_requirements(tmp_path: Path):
    """Verify current port inheritance view exposes declared derived artifacts."""
    write_package(
        tmp_path / "model.sysml",
        """
        requirement def ReqA { doc /* Requirement A */ }

        port def BasePort {
          attribute width = 8;
          requirement reqA : ReqA;
        }

        port def DerivedPort specializes BasePort {
          attribute gain = 2.0;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    assert_architecture_structure(
        architecture,
        """
        package Example
        port BasePort
          attr width:Integer=8
          req reqA:ReqA -> ReqA
        port DerivedPort specializes BasePort
          attr gain:Real=2.0
        requirement ReqA
          attr text:String='Requirement A'
        """,
    )
