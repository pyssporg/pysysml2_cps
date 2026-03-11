import pytest

from pycps_sysmlv2 import (
    NodeType,
    SysMLConnection,
    SysMLPackage,
    SysMLPartDefinition,
    SysMLPartReference,
    SysMLPortDefinition,
    SysMLPortReference,
    SysMLRequirementDefinition,
    SysMLRequirementReference,
)


def test_architecture_add_remove_definitions():
    """Verify package-level add/remove APIs mutate definition registries correctly."""
    architecture = SysMLPackage(name="Example", package="Example")
    part_def = SysMLPartDefinition(name="System")
    port_def = SysMLPortDefinition(name="Signal")
    req_def = SysMLRequirementDefinition(name="ReqA")
    req_def.text = "Requirement A"

    architecture.add_def(NodeType.Part, part_def.name, part_def)
    architecture.add_def(NodeType.Port, port_def.name, port_def)
    architecture.add_def(NodeType.Requirement, req_def.name, req_def)

    assert architecture.get_def(NodeType.Part, "System") is part_def
    assert architecture.get_def(NodeType.Port, "Signal") is port_def
    assert architecture.get_def(NodeType.Requirement, "ReqA") is req_def

    architecture.remove_def(NodeType.Part, "System")
    architecture.remove_def(NodeType.Port, "Signal")
    architecture.remove_def(NodeType.Requirement, "ReqA")
    assert architecture.part_definitions == {}
    assert architecture.port_definitions == {}
    assert architecture.requirement_definitions == {}


def test_part_definition_add_remove_references_and_connections():
    """Verify part definitions can add/remove refs and connections via NodeType APIs."""
    system_def = SysMLPartDefinition(name="System")
    child_def = SysMLPartDefinition(name="Child")
    signal_def = SysMLPortDefinition(name="Signal")
    req_def = SysMLRequirementDefinition(name="ReqA")

    part_ref = SysMLPartReference(name="child", type="Child", ref_node=child_def)
    port_ref = SysMLPortReference(
        name="input", direction="in", type="Signal", ref_node=signal_def
    )
    req_ref = SysMLRequirementReference(name="reqA", type="ReqA", ref_node=req_def)
    connection = SysMLConnection(
        name="child_out_to_child_in",
        src_part="child",
        src_port="out",
        dst_part="child",
        dst_port="in",
    )

    system_def.add_ref(NodeType.Part, "child", part_ref)
    system_def.add_ref(NodeType.Port, "input", port_ref)
    system_def.add_ref(NodeType.Requirement, "reqA", req_ref)
    system_def.add_def(NodeType.Connection, connection.key, connection)

    assert system_def.refs(NodeType.Part)["child"] is part_ref
    assert system_def.refs(NodeType.Port)["input"] is port_ref
    assert system_def.refs(NodeType.Requirement)["reqA"] is req_ref
    assert system_def.defs(NodeType.Connection)[connection.key] is connection

    system_def.remove_ref(NodeType.Part, "child")
    system_def.remove_ref(NodeType.Port, "input")
    system_def.remove_ref(NodeType.Requirement, "reqA")
    system_def.remove_def(NodeType.Connection, connection.key)
    assert system_def.refs(NodeType.Part) == {}
    assert system_def.refs(NodeType.Port) == {}
    assert system_def.refs(NodeType.Requirement) == {}
    assert system_def.defs(NodeType.Connection) == {}


def test_port_definition_add_remove_requirement_references():
    """Verify port definitions can add/remove requirement references via NodeType APIs."""
    port_def = SysMLPortDefinition(name="Signal")
    req_def = SysMLRequirementDefinition(name="ReqA")
    req_ref = SysMLRequirementReference(name="reqA", type="ReqA", ref_node=req_def)
    port_def.add_ref(NodeType.Requirement, "reqA", req_ref)

    assert port_def.refs(NodeType.Requirement)["reqA"] is req_ref
    port_def.remove_ref(NodeType.Requirement, "reqA")
    assert port_def.refs(NodeType.Requirement) == {}


def test_get_def_traverses_parent_namespaces():
    """Verify definition lookup walks parent namespaces when a child lacks the key."""
    architecture = SysMLPackage(name="Example", package="Example")
    system_def = SysMLPartDefinition(name="System", parent=architecture)
    signal_def = SysMLPortDefinition(name="Signal")
    architecture.add_def(NodeType.Port, signal_def.name, signal_def)

    assert system_def.get_def(NodeType.Port, "Signal") is signal_def


def test_container_access_rejects_unsupported_node_types():
    """Verify defs/refs reject node kinds unsupported by the receiving container."""
    architecture = SysMLPackage(name="Example", package="Example")
    system_def = SysMLPartDefinition(name="System")

    with pytest.raises(KeyError, match="Unsupported ref type"):
        architecture.refs(NodeType.Part)
    with pytest.raises(KeyError, match="Unsupported def type"):
        architecture.defs(NodeType.Connection)


def test_add_def_and_add_ref_warn_on_overwrite():
    """Verify duplicate inserts emit overwrite warnings on mutable containers."""
    system_def = SysMLPartDefinition(name="System")
    first_ref = SysMLPartReference(name="child", type="Child")
    second_ref = SysMLPartReference(name="child", type="OtherChild")

    with pytest.warns(UserWarning, match="Overwriting existing definition: child"):
        system_def.add_def(NodeType.Connection, "child", SysMLConnection(name="a", src_part="x", src_port="y", dst_part="z", dst_port="w"))
        system_def.add_def(NodeType.Connection, "child", SysMLConnection(name="b", src_part="x", src_port="y", dst_part="z", dst_port="w"))

    with pytest.warns(UserWarning, match="Overwriting existing reference: child"):
        system_def.add_ref(NodeType.Part, "child", first_ref)
        system_def.add_ref(NodeType.Part, "child", second_ref)
