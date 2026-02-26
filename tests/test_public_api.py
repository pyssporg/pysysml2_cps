import json
from dataclasses import fields, is_dataclass
from pathlib import Path

from pycps_sysmlv2 import (
    load_architecture,
)
from pycps_sysmlv2.definitions import PrimitiveType, SysMLType

from pycps_sysmlv2.parser_utils import json_dumps


FIXTURE_ARCH_DIR = Path(__file__).resolve().parent / "fixtures" / "aircraft_subset"
FIXTURE_REFERENCE_JSON = FIXTURE_ARCH_DIR / "architecture_reference.json"


def test_architecture_loader_from_fixture_directory():
    architecture = load_architecture(FIXTURE_ARCH_DIR)
    composition = architecture.part_definitions["AircraftComposition"]
    assert architecture.package == "Aircraft"
    assert set(architecture.part_definitions) == {
        "AircraftBaseComposition",
        "AutopilotModule",
        "MissionComputer",
        "Environment",
        "AircraftComposition",
    }
    assert set(architecture.port_definitions) == {
        "PilotCommand",
        "OrientationEuler",
        "PositionXYZ",
        "FlightStatusPacket",
        "MissionStatus",
    }
    assert len(composition.connections) == 5
    assert len(architecture.requirements) == 2
    assert composition.base_part_name == "AircraftBaseComposition"
    assert composition.attributes["profile"].value == "operational"
    assert composition.attributes["variant"].value == "f16"
    assert "obsolete" not in composition.attributes

    # Keep a checked-in JSON snapshot of the parsed fixture for easy diffing.
    FIXTURE_REFERENCE_JSON.write_text(json_dumps(architecture, []))


def test_architecture_loader_from_fixture_file():
    arch_file = FIXTURE_ARCH_DIR / "part_definitions.sysml"
    architecture = load_architecture(arch_file)
    assert architecture.package == "Aircraft"
    assert "AutopilotModule" in architecture.part_definitions


def test_ports_are_linked_to_payload_definitions():
    architecture = load_architecture(FIXTURE_ARCH_DIR)
    autopilot = architecture.part_definitions["AutopilotModule"]
    by_name = autopilot.ports
    assert by_name["autopilotCmd"].port_name == "PilotCommand"
    assert by_name["autopilotCmd"].port_def is not None
    assert by_name["autopilotCmd"].port_def.name == "PilotCommand"
    assert by_name["feedbackBus"].port_def is not None
    assert by_name["feedbackBus"].port_def.name == "FlightStatusPacket"


def test_extracted_attribute_literals_are_parseable():
    architecture = load_architecture(FIXTURE_ARCH_DIR)
    waypoint_attr = architecture.part_definitions["AutopilotModule"].attributes["waypointX_km"]
    assert waypoint_attr.value == [0.0, 10.0, 20.0]
    assert isinstance(waypoint_attr.type, SysMLType)
    assert waypoint_attr.type.primitive_type() == PrimitiveType.Real
    assert architecture.part_definitions["AutopilotModule"].attributes["waypointCount"].value == 10


def test_subparts_are_linked_to_part_definitions():
    architecture = load_architecture(FIXTURE_ARCH_DIR)
    aircraft = architecture.part_definitions["AircraftComposition"]
    by_name = aircraft.parts

    assert by_name["autopilot"].part_name == "AutopilotModule"
    assert by_name["autopilot"].part_def is not None
    assert by_name["autopilot"].part_def.name == "AutopilotModule"

    assert by_name["missionComputer"].part_def is not None
    assert by_name["missionComputer"].part_def.name == "MissionComputer"

    assert by_name["environment"].part_def is not None
    assert by_name["environment"].part_def.name == "Environment"


def test_connections_are_linked_to_part_and_port_definitions():
    architecture = load_architecture(FIXTURE_ARCH_DIR)
    composition = architecture.part_definitions["AircraftComposition"]

    first = composition.connections[0]
    assert first.src_component == "autopilot"
    assert first.src_port == "autopilotCmd"
    assert first.dst_component == "missionComputer"
    assert first.dst_port == "autopilotInput"

    assert first.src_part_def is not None
    assert first.src_part_def.name == "AutopilotModule"
    assert first.dst_part_def is not None
    assert first.dst_part_def.name == "MissionComputer"

    assert first.src_port_def is not None
    assert first.src_port_def.name == "PilotCommand"

    assert first.dst_port_def is not None
    assert first.dst_port_def.name == "PilotCommand"


def test_part_inheritance_supports_add_replace_remove(tmp_path: Path):
    model = tmp_path / "model.sysml"
    model.write_text(
        """
        package Example {
          port def Signal {}
          port def AltSignal {}

          part def ChildA {
            in port data : Signal;
          }

          part def ChildB {
            out port data : Signal;
          }

          part def Base {
            attribute keepMe = 1;
            attribute replaceMe = 10;
            in port oldIn : Signal;
            out port replacePort : Signal;
            part left : ChildA;
            part right : ChildB;
            connect left.data to right.data;
          }

          part def Derived : Base {
            remove attribute keepMe;
            remove port oldIn;
            remove connect left.data to right.data;

            replace attribute replaceMe = 99;
            replace out port replacePort : AltSignal;
            replace part right : ChildA;

            attribute added = true;
            in port newIn : Signal;
            part extra : ChildB;
            connect right.data to extra.data;
          }
        }
        """.strip()
        + "\n"
    )

    arch = load_architecture(tmp_path)
    derived = arch.part_definitions["Derived"]

    assert derived.base_part_name == "Base"
    assert derived.base_part_def is not None
    assert derived.base_part_def.name == "Base"

    assert "keepMe" not in derived.attributes
    assert derived.attributes["replaceMe"].value == 99
    assert derived.attributes["added"].value is True

    assert "oldIn" not in derived.ports
    assert derived.ports["replacePort"].port_name == "AltSignal"
    assert derived.ports["newIn"].port_name == "Signal"

    assert derived.parts["right"].part_name == "ChildA"
    assert "extra" in derived.parts
    assert len(derived.connections) == 1
    c = derived.connections[0]
    assert (c.src_component, c.src_port, c.dst_component, c.dst_port) == (
        "right",
        "data",
        "extra",
        "data",
    )
