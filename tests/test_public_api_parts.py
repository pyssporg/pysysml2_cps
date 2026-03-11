from pathlib import Path

from pycps_sysmlv2 import SysMLParser

from public_api_test_utils import (
    assert_architecture_structure,
    write_package,
)


def test_attribute_literals_are_parsed(tmp_path: Path):
    """Verify literal-valued attributes are parsed with inferred types."""
    write_package(
        tmp_path / "model.sysml",
        """
        part def Node {
          attribute values = [1.0, 2.0, 3.0];
          attribute count = 3;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    assert_architecture_structure(
        architecture,
        """
        package Example
        part Node
          attr count:Integer=3
          attr values:List[Real]=[1.0, 2.0, 3.0]
        """,
    )


def test_typed_attributes_without_values_are_parsed(tmp_path: Path):
    """Verify typed attributes without literals retain type and null value."""
    write_package(
        tmp_path / "model.sysml",
        """
        part def Node {
          attribute gain : float64;
          attribute enabled : boolean;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    assert_architecture_structure(
        architecture,
        """
        package Example
        part Node
          attr enabled:Boolean=None
          attr gain:Real=None
        """,
    )


def test_subpart_reference_links_to_part_definition(tmp_path: Path):
    """Verify subpart usages resolve to their part definition nodes."""
    write_package(
        tmp_path / "model.sysml",
        """
        part def Child {}

        part def System {
          part child : Child;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    assert_architecture_structure(
        architecture,
        """
        package Example
        part Child
        part System
          part child:Child -> Child
        """,
    )


def test_doc_comments_are_attached_to_definitions(tmp_path: Path):
    """Verify doc comments attach to the intended definitions and members."""
    write_package(
        tmp_path / "model.sysml",
        """
        port def Signal {
          doc /* signal docs */
          doc /* payload docs */
          attribute p = 1;
        }

        part def Node {
          doc /* node docs */
          doc /* attribute docs */
          attribute threshold = 2;
          doc /* input docs */
          in port input : Signal;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    assert_architecture_structure(
        architecture,
        """
        package Example
        part Node doc="node docs"
          attr threshold:Integer=2 doc="attribute docs"
          port in input:Signal -> Signal doc="input docs"
        port Signal doc="signal docs"
          attr p:Integer=1 doc="payload docs"
        """,
    )
