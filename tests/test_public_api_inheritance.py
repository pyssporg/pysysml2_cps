from pathlib import Path

import pytest

from pycps_sysmlv2 import SysMLParser

from public_api_test_utils import (
    assert_architecture_structure,
    write_package,
)


def test_part_inheritance_removes_attributes(tmp_path: Path):
    """Verify part inheritance removes inherited attributes from the resolved view."""
    write_package(
        tmp_path / "model.sysml",
        """
        part def Base {
          attribute remove_attr = 1;
        }

        part def Derived specializes Base {
          remove attribute remove_attr;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    assert_architecture_structure(
        architecture,
        """
        package Example
        part Base
          attr remove_attr:Integer=1
        part Derived specializes Base
        """,
    )


def test_part_inheritance_redefines_attributes(tmp_path: Path):
    """Verify part inheritance redefines inherited attributes in the resolved view."""
    write_package(
        tmp_path / "model.sysml",
        """
        part def Base {
          attribute replace_attr = 2;
        }

        part def Derived specializes Base {
          redefines attribute replace_attr = 99;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    assert_architecture_structure(
        architecture,
        """
        package Example
        part Base
          attr replace_attr:Integer=2
        part Derived specializes Base
          attr replace_attr:Integer=99
        """,
    )


def test_part_inheritance_adds_attributes(tmp_path: Path):
    """Verify part inheritance adds new attributes alongside inherited structure."""
    write_package(
        tmp_path / "model.sysml",
        """
        part def Base {}

        part def Derived specializes Base {
          attribute add_attr = true;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    assert_architecture_structure(
        architecture,
        """
        package Example
        part Base
        part Derived specializes Base
          attr add_attr:Boolean=True
        """,
    )


def test_part_inheritance_removes_ports(tmp_path: Path):
    """Verify part inheritance removes inherited ports from the resolved view."""
    write_package(
        tmp_path / "model.sysml",
        """
        port def SignalA {}

        part def Base {
          out port remove_port : SignalA;
        }

        part def Derived specializes Base {
          remove port remove_port;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    assert_architecture_structure(
        architecture,
        """
        package Example
        part Base
          port out remove_port:SignalA -> SignalA
        part Derived specializes Base
        port SignalA
        """,
    )


def test_part_inheritance_redefines_ports(tmp_path: Path):
    """Verify part inheritance redefines inherited ports in the resolved view."""
    write_package(
        tmp_path / "model.sysml",
        """
        port def SignalA {}
        port def SignalB {}

        part def Base {
          out port replace_port : SignalA;
        }

        part def Derived specializes Base {
          redefines out port replace_port : SignalB;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    assert_architecture_structure(
        architecture,
        """
        package Example
        part Base
          port out replace_port:SignalA -> SignalA
        part Derived specializes Base
          port out replace_port:SignalB -> SignalB
        port SignalA
        port SignalB
        """,
    )


def test_part_inheritance_adds_ports(tmp_path: Path):
    """Verify part inheritance adds new ports alongside inherited structure."""
    write_package(
        tmp_path / "model.sysml",
        """
        port def SignalA {}

        part def Base {}

        part def Derived specializes Base {
          out port add_port : SignalA;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    assert_architecture_structure(
        architecture,
        """
        package Example
        part Base
        part Derived specializes Base
          port out add_port:SignalA -> SignalA
        port SignalA
        """,
    )


def test_part_inheritance_redefines_part_references(tmp_path: Path):
    """Verify part inheritance redefines inherited child part references."""
    write_package(
        tmp_path / "model.sysml",
        """
        part def ChildA {}
        part def ChildB {}

        part def Base {
          part right : ChildB;
        }

        part def Derived specializes Base {
          redefines part right : ChildA;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    assert_architecture_structure(
        architecture,
        """
        package Example
        part Base
          part right:ChildB -> ChildB
        part ChildA
        part ChildB
        part Derived specializes Base
          part right:ChildA -> ChildA
        """,
    )


def test_part_inheritance_adds_part_references(tmp_path: Path):
    """Verify part inheritance adds new child part references."""
    write_package(
        tmp_path / "model.sysml",
        """
        part def ChildB {}

        part def Base {}

        part def Derived specializes Base {
          part extra : ChildB;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    assert_architecture_structure(
        architecture,
        """
        package Example
        part Base
        part ChildB
        part Derived specializes Base
          part extra:ChildB -> ChildB
        """,
    )


def test_part_inheritance_removes_requirements(tmp_path: Path):
    """Verify part inheritance removes inherited requirement usages."""
    write_package(
        tmp_path / "model.sysml",
        """
        requirement def ReqA { doc /* Base req */ }

        part def Base {
          requirement keep_req : ReqA;
        }

        part def Derived specializes Base {
          remove requirement keep_req;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    assert_architecture_structure(
        architecture,
        """
        package Example
        part Base
          req keep_req:ReqA -> ReqA
        part Derived specializes Base
        requirement ReqA
          attr text:String='Base req'
        """,
    )


def test_part_inheritance_redefines_requirements(tmp_path: Path):
    """Verify part inheritance redefines inherited requirement usages."""
    write_package(
        tmp_path / "model.sysml",
        """
        requirement def ReqA { doc /* Base req */ }
        requirement def ReqB { doc /* Alt req */ }

        part def Base {
          requirement replace_req : ReqA;
        }

        part def Derived specializes Base {
          redefines requirement replace_req : ReqB;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    assert_architecture_structure(
        architecture,
        """
        package Example
        part Base
          req replace_req:ReqA -> ReqA
        part Derived specializes Base
          req replace_req:ReqB -> ReqB
        requirement ReqA
          attr text:String='Base req'
        requirement ReqB
          attr text:String='Alt req'
        """,
    )


def test_part_inheritance_adds_requirements(tmp_path: Path):
    """Verify part inheritance adds new requirement usages."""
    write_package(
        tmp_path / "model.sysml",
        """
        requirement def ReqA { doc /* Base req */ }

        part def Base {}

        part def Derived specializes Base {
          requirement add_req : ReqA;
        }
        """,
    )

    architecture = SysMLParser(tmp_path).parse()
    assert_architecture_structure(
        architecture,
        """
        package Example
        part Base
        part Derived specializes Base
          req add_req:ReqA -> ReqA
        requirement ReqA
          attr text:String='Base req'
        """,
    )


def test_part_inheritance_remove_connection_then_add_new_connection(tmp_path: Path):
    """Verify unresolved inherited subparts in derived connections currently raise a linking error."""
    write_package(
        tmp_path / "model.sysml",
        """
        port def Signal {}

        part def A {
          out port out_signal : Signal;
        }

        part def B {
          in port in_signal : Signal;
        }

        part def C {
          in port in_signal : Signal;
        }

        part def Base {
          part a : A;
          part b : B;
          part c : C;
          connect a.out_signal to b.in_signal;
        }

        part def Derived specializes Base {
          remove connect a.out_signal to b.in_signal;
          connect a.out_signal to c.in_signal;
        }
        """,
    )

    with pytest.raises(ValueError, match="Subpart not found for connection: Derived.a"):
        SysMLParser(tmp_path).parse()
