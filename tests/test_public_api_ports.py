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


def test_port_inheritance_removes_requirements(tmp_path: Path):
    """Verify port inheritance removes inherited requirement usages."""
    write_package(
        tmp_path / "model.sysml",
        """
        requirement def ReqA { doc /* Requirement A */ }

        port def BasePort {
          requirement reqA : ReqA;
        }

        port def DerivedPort specializes BasePort {
          remove requirement reqA;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    assert_architecture_structure(
        architecture,
        """
        package Example
        port BasePort
          req reqA:ReqA -> ReqA
        port DerivedPort specializes BasePort
        requirement ReqA
          attr text:String='Requirement A'
        """,
    )


def test_port_inheritance_redefines_attributes_and_requirements(tmp_path: Path):
    """Verify port inheritance redefines inherited members in the resolved view."""
    write_package(
        tmp_path / "model.sysml",
        """
        requirement def ReqA { doc /* Requirement A */ }
        requirement def ReqB { doc /* Requirement B */ }

        port def BasePort {
          attribute width = 8;
          requirement reqA : ReqA;
        }

        port def DerivedPort specializes BasePort {
          redefines attribute width = 16;
          redefines requirement reqA : ReqB;
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
          attr width:Integer=16
          req reqA:ReqB -> ReqB
        requirement ReqA
          attr text:String='Requirement A'
        requirement ReqB
          attr text:String='Requirement B'
        """,
    )
