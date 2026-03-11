import pytest

from pycps_sysmlv2.definitions import PrimitiveType, SysMLAttribute, SysMLType


@pytest.mark.parametrize(
    ("value", "expected_primitive"),
    [
        (True, PrimitiveType.Boolean),
        (42, PrimitiveType.Integer),
        (3.14, PrimitiveType.Real),
        ("abc", PrimitiveType.String),
        (None, PrimitiveType.Null),
    ],
)
def test_sysml_type_from_value_identifies_python_primitives(value, expected_primitive):
    """Verify primitive Python literals map to expected SysML primitive types."""
    sysml_type = SysMLType.from_value(value)
    assert isinstance(sysml_type, SysMLType)
    assert sysml_type.type == expected_primitive
    assert sysml_type.primitive_type() == expected_primitive


@pytest.mark.parametrize(
    ("type_name", "expected_primitive"),
    [
        ("real", PrimitiveType.Real),
        ("float64", PrimitiveType.Real),
        ("int", PrimitiveType.Integer),
        ("boolean", PrimitiveType.Boolean),
        ("string", PrimitiveType.String),
    ],
)
def test_sysml_type_from_string_maps_known_type_aliases(type_name, expected_primitive):
    """Verify known type-name aliases normalize to the expected SysML primitive."""
    parsed = SysMLType.from_string(type_name)
    assert isinstance(parsed, SysMLType)
    assert parsed.type == expected_primitive


@pytest.mark.parametrize(
    ("literal", "expected_value", "expected_primitive"),
    [
        (None, None, PrimitiveType.Null),
        ("", None, PrimitiveType.Null),
        ("   ", None, PrimitiveType.Null),
        ("true", True, PrimitiveType.Boolean),
        ("FALSE", False, PrimitiveType.Boolean),
        ("42", 42, PrimitiveType.Integer),
        ("3.5", 3.5, PrimitiveType.Real),
        ("[3.5, 7]", [3.5, 7], [PrimitiveType.Real]),
        ('"quoted"', "quoted", PrimitiveType.String),
        ("unquoted_text", "unquoted_text", PrimitiveType.String),
    ],
)
def test_sysml_attribute_from_literal_infers_value_and_sysml_type(
    literal, expected_value, expected_primitive
):
    """Verify attribute literal parsing infers both value and SysML type."""
    attr = SysMLAttribute.from_literal(name="x", value=literal, doc=None)
    assert attr.name == "x"
    assert attr.value == expected_value
    assert isinstance(attr.type, SysMLType)
    assert attr.type.type == expected_primitive
