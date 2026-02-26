import json
from dataclasses import fields, is_dataclass
from pathlib import Path

from pycps_sysmlv2 import (
    load_architecture,
)
from pycps_sysmlv2.definitions import PrimitiveType, SysMLType

from pycps_sysmlv2.parser_utils import json_dumps


FIXTURE_A_DIR = Path(__file__).resolve().parent / "fixtures" / "fixture_a"
FIXTURE_A_REFERENCE_JSON = FIXTURE_A_DIR / "architecture_reference.json"
FIXTURE_B_DIR = Path(__file__).resolve().parent / "fixtures" / "fixture_b"
FIXTURE_B_REFERENCE_JSON = FIXTURE_B_DIR / "architecture_reference.json"


def test_architecture_loader_from_fixture_directory():
    architecture = load_architecture(FIXTURE_A_DIR)
    composition = architecture.part_definitions["FixtureAComposition"]
    assert architecture.package == "FixtureA"
    assert set(architecture.part_definitions) == {
        "ChildA",
        "ChildB",
        "ChildC",
        "FixtureAComposition",
    }
    assert set(architecture.port_definitions) == {
        "SignalA",
        "SignalB",
    }
    assert len(composition.connections) == 2
    assert len(architecture.requirements) == 2

    # Keep a checked-in JSON snapshot of the parsed fixture for easy diffing.
    FIXTURE_A_REFERENCE_JSON.write_text(json_dumps(architecture, []))


def test_architecture_loader_from_fixture_file():
    arch_file = FIXTURE_A_DIR / "part_definitions.sysml"
    architecture = load_architecture(arch_file)
    assert architecture.package == "FixtureA"
    assert "ChildA" in architecture.part_definitions


def test_ports_are_linked_to_payload_definitions():
    architecture = load_architecture(FIXTURE_A_DIR)
    child_a = architecture.part_definitions["ChildA"]
    by_name = child_a.ports
    assert by_name["inA"].port_name == "SignalA"
    assert by_name["inA"].port_def is not None
    assert by_name["inA"].port_def.name == "SignalA"
    assert by_name["outB"].port_def is not None
    assert by_name["outB"].port_def.name == "SignalB"


def test_extracted_attribute_literals_are_parseable():
    architecture = load_architecture(FIXTURE_A_DIR)
    values_attr = architecture.part_definitions["ChildA"].attributes["valuesA"]
    assert values_attr.value == [1.0, 2.0, 3.0]
    assert isinstance(values_attr.type, SysMLType)
    assert values_attr.type.primitive_type() == PrimitiveType.Real
    assert architecture.part_definitions["ChildA"].attributes["countA"].value == 3


def test_subparts_are_linked_to_part_definitions():
    architecture = load_architecture(FIXTURE_A_DIR)
    fixture_a = architecture.part_definitions["FixtureAComposition"]
    by_name = fixture_a.parts

    assert by_name["leftA"].part_name == "ChildA"
    assert by_name["leftA"].part_def is not None
    assert by_name["leftA"].part_def.name == "ChildA"

    assert by_name["rightB"].part_def is not None
    assert by_name["rightB"].part_def.name == "ChildB"

    assert by_name["sourceC"].part_def is not None
    assert by_name["sourceC"].part_def.name == "ChildC"


def test_connections_are_linked_to_part_and_port_definitions():
    architecture = load_architecture(FIXTURE_A_DIR)
    composition = architecture.part_definitions["FixtureAComposition"]

    first = composition.connections[0]
    assert first.src_component == "leftA"
    assert first.src_port == "outB"
    assert first.dst_component == "rightB"
    assert first.dst_port == "inB"

    assert first.src_part_def is not None
    assert first.src_part_def.name == "ChildA"
    assert first.dst_part_def is not None
    assert first.dst_part_def.name == "ChildB"

    assert first.src_port_def is not None
    assert first.src_port_def.name == "SignalB"

    assert first.dst_port_def is not None
    assert first.dst_port_def.name == "SignalB"


def test_part_inheritance_supports_add_replace_remove():
    arch = load_architecture(FIXTURE_B_DIR)
    derived = arch.part_definitions["FixtureB"]

    assert derived.base_part_name == "FixtureBBase"
    assert derived.base_part_def is not None
    assert derived.base_part_def.name == "FixtureBBase"

    assert "removeA" not in derived.attributes
    assert derived.attributes["replaceA"].value == 99
    assert derived.attributes["addA"].value is True

    assert "removePortA" not in derived.ports
    assert derived.ports["replacePortA"].port_name == "SignalB"
    assert derived.ports["addPortA"].port_name == "SignalA"

    assert derived.parts["rightB"].part_name == "ChildA"
    assert "extraB" in derived.parts
    assert len(derived.connections) == 1
    c = derived.connections[0]
    assert (c.src_component, c.src_port, c.dst_component, c.dst_port) == (
        "rightB",
        "outA",
        "extraB",
        "inA",
    )

    FIXTURE_B_REFERENCE_JSON.write_text(json_dumps(arch, []))
