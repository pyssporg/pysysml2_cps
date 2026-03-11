from pycps_sysmlv2 import (
    SysMLPackage,
    SysMLPartDefinition,
    SysMLPortDefinition,
    SysMLRequirementDefinition,
)


def test_architecture_add_remove_definitions():
    architecture = SysMLPackage(name="Example", package="Example")
    part_def = SysMLPartDefinition(name="System")
    port_def = SysMLPortDefinition(name="Signal")
    req_def = SysMLRequirementDefinition(name="ReqA")
    req_def.text = "Requirement A"

    architecture.add_part(part_def)
    architecture.add_port(port_def)
    architecture.add_requirement(req_def)

    assert architecture.get_part("System") is part_def
    assert architecture.get_port("Signal") is port_def
    assert architecture.get_requirement("ReqA") is req_def

    assert architecture.remove_part("System") is part_def
    assert architecture.remove_port("Signal") is port_def
    assert architecture.remove_requirement("ReqA") is req_def


def test_part_definition_add_remove_references_and_connections():
    system_def = SysMLPartDefinition(name="System")
    child_def = SysMLPartDefinition(name="Child")
    signal_def = SysMLPortDefinition(name="Signal")
    req_def = SysMLRequirementDefinition(name="ReqA")

    part_ref = system_def.add_part("child", "Child", part_def=child_def)
    port_ref = system_def.add_port("input", "in", "Signal", port_def=signal_def)
    req_ref = system_def.add_requirement("reqA", "ReqA", requirement_def=req_def)
    connection = system_def.add_connection("child", "out", "child", "in")

    assert system_def.parts["child"] is part_ref
    assert system_def.ports["input"] is port_ref
    assert system_def.refs["requirements"]["reqA"] is req_ref
    assert system_def.connections[0] is connection

    assert system_def.remove_part("child") is part_ref
    assert system_def.remove_port("input") is port_ref
    assert system_def.remove_requirement("reqA") is req_ref
    assert system_def.remove_connection("child", "out", "child", "in") is connection


def test_port_definition_add_remove_requirement_references():
    port_def = SysMLPortDefinition(name="Signal")
    req_def = SysMLRequirementDefinition(name="ReqA")
    req_ref = port_def.add_requirement("reqA", "ReqA", requirement_def=req_def)

    assert port_def.requirements["reqA"] is req_ref
    assert port_def.remove_requirement("reqA") is req_ref
