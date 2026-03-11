from pathlib import Path

import pytest

from pycps_sysmlv2 import SysMLParser

from public_api_test_utils import (
    assert_architecture_structure,
    write_package,
)


def test_part_inheritance_add_replace_remove(tmp_path: Path):
    """Verify part inheritance applies remove/redefine/add semantics on resolved views."""
    write_package(
        tmp_path / "model.sysml",
        """
        requirement def ReqA { doc /* Base req */ }
        requirement def ReqB { doc /* Alt req */ }

        port def SignalA {}
        port def SignalB {}

        part def ChildA {
          out port out_a : SignalA;
        }

        part def ChildB {
          in port in_b : SignalA;
        }

        part def Base {
          attribute remove_attr = 1;
          attribute replace_attr = 2;

          out port remove_port : SignalA;
          out port replace_port : SignalA;

          part left : ChildA;
          part right : ChildB;

          requirement keep_req : ReqA;
          requirement replace_req : ReqA;
        }

        part def Derived specializes Base {
          remove attribute remove_attr;
          redefines attribute replace_attr = 99;
          attribute add_attr = true;

          remove port remove_port;
          redefines out port replace_port : SignalB;
          out port add_port : SignalA;

          redefines part right : ChildA;
          part extra : ChildB;
          connect right.out_a to extra.in_b;

          remove requirement keep_req;
          redefines requirement replace_req : ReqB;
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
          attr remove_attr:Integer=1
          attr replace_attr:Integer=2
          part left:ChildA -> ChildA
          part right:ChildB -> ChildB
          port out remove_port:SignalA -> SignalA
          port out replace_port:SignalA -> SignalA
          req keep_req:ReqA -> ReqA
          req replace_req:ReqA -> ReqA
        part ChildA
          port out out_a:SignalA -> SignalA
        part ChildB
          port in in_b:SignalA -> SignalA
        part Derived specializes Base
          attr add_attr:Boolean=True
          attr replace_attr:Integer=99
          part extra:ChildB -> ChildB
          part right:ChildA -> ChildA
          port out add_port:SignalA -> SignalA
          port out replace_port:SignalB -> SignalB
          req add_req:ReqA -> ReqA
          req replace_req:ReqB -> ReqB
          connect right.out_a -> extra.in_b
        port SignalA
        port SignalB
        requirement ReqA
          attr text:String='Base req'
        requirement ReqB
          attr text:String='Alt req'
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
