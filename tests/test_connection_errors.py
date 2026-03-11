from pathlib import Path

import pytest

from pycps_sysmlv2 import NodeType, SysMLConnection, SysMLPartDefinition, SysMLPartReference, SysMLPortDefinition, SysMLPortReference, SysMLParser
from pycps_sysmlv2.parser.linking import attach_connection_definitions

from public_api_test_utils import write_package


def test_connection_to_missing_source_port_fails_with_context(tmp_path: Path):
    """Verify connections fail when the source subpart does not expose the named port."""
    write_package(
        tmp_path / "model.sysml",
        """
        port def Signal {}

        part def Source {}

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

    with pytest.raises(ValueError, match="Port not found for connection: Source.out_signal"):
        SysMLParser(tmp_path).parse()


def test_connection_to_missing_destination_port_fails_with_context(tmp_path: Path):
    """Verify connections fail when the destination subpart does not expose the named port."""
    write_package(
        tmp_path / "model.sysml",
        """
        port def Signal {}

        part def Source {
          out port out_signal : Signal;
        }

        part def Sink {}

        part def System {
          part src : Source;
          part dst : Sink;
          connect src.out_signal to dst.in_signal;
        }
        """,
    )

    with pytest.raises(ValueError, match="Port not found for connection: Sink.in_signal"):
        SysMLParser(tmp_path).parse()


def test_linker_reports_unresolved_source_endpoint_port_definition():
    """Verify the connection linker reports unresolved source endpoint port definitions."""
    signal_ref = SysMLPortReference(name="out_signal", direction="out", type="Signal")
    source_def = SysMLPartDefinition(name="Source")
    source_def.add_ref(NodeType.Port, "out_signal", signal_ref)

    src_ref = SysMLPartReference(name="src", type="Source", ref_node=source_def)
    dst_ref = SysMLPartReference(name="dst", type="Sink", ref_node=SysMLPartDefinition(name="Sink"))
    sink_port = SysMLPortReference(
        name="in_signal",
        direction="in",
        type="Signal",
        ref_node=SysMLPortDefinition(name="Signal"),
    )
    dst_ref.ref_node.add_ref(NodeType.Port, "in_signal", sink_port)

    system = SysMLPartDefinition(name="System")
    system.add_ref(NodeType.Part, "src", src_ref)
    system.add_ref(NodeType.Part, "dst", dst_ref)
    connection = SysMLConnection(
        name="src_to_dst",
        src_part="src",
        src_port="out_signal",
        dst_part="dst",
        dst_port="in_signal",
    )
    system.add_def(NodeType.Connection, connection.key, connection)

    with pytest.raises(
        ValueError,
        match="Port definition not found for connection endpoint: Source.out_signal",
    ):
        attach_connection_definitions({"System": system})


def test_linker_reports_unresolved_destination_endpoint_port_definition():
    """Verify the connection linker reports unresolved destination endpoint port definitions."""
    source_def = SysMLPartDefinition(name="Source")
    source_def.add_ref(
        NodeType.Port,
        "out_signal",
        SysMLPortReference(
            name="out_signal",
            direction="out",
            type="Signal",
            ref_node=SysMLPortDefinition(name="Signal"),
        ),
    )
    sink_def = SysMLPartDefinition(name="Sink")
    sink_def.add_ref(NodeType.Port, "in_signal", SysMLPortReference(name="in_signal", direction="in", type="Signal"))

    system = SysMLPartDefinition(name="System")
    system.add_ref(NodeType.Part, "src", SysMLPartReference(name="src", type="Source", ref_node=source_def))
    system.add_ref(NodeType.Part, "dst", SysMLPartReference(name="dst", type="Sink", ref_node=sink_def))
    connection = SysMLConnection(
        name="src_to_dst",
        src_part="src",
        src_port="out_signal",
        dst_part="dst",
        dst_port="in_signal",
    )
    system.add_def(NodeType.Connection, connection.key, connection)

    with pytest.raises(
        ValueError,
        match="Port definition not found for connection endpoint: Sink.in_signal",
    ):
        attach_connection_definitions({"System": system})
