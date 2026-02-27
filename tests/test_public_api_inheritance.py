from pathlib import Path

from pycps_sysmlv2 import load_architecture

from public_api_test_utils import write_model, write_reference


def test_part_inheritance_add_replace_remove(tmp_path: Path):
    write_model(
        tmp_path / "model.sysml",
        """
        package Example {
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
          }

          part def Derived : Base {
            remove attribute remove_attr;
            replace attribute replace_attr = 99;
            attribute add_attr = true;

            remove port remove_port;
            replace out port replace_port : SignalB;
            out port add_port : SignalA;

            replace part right : ChildA;
            part extra : ChildB;
            connect right.out_a to extra.in_b;
          }
        }
        """,
    )

    architecture = load_architecture(tmp_path)
    derived = architecture.part_definitions["Derived"]

    assert derived.base_part_name == "Base"
    assert derived.base_part_def is not None
    assert derived.base_part_def.name == "Base"

    assert "remove_attr" not in derived.attributes
    assert derived.attributes["replace_attr"].value == 99
    assert derived.attributes["add_attr"].value is True

    assert "remove_port" not in derived.ports
    assert derived.ports["replace_port"].port_name == "SignalB"
    assert derived.ports["add_port"].port_name == "SignalA"

    assert derived.parts["right"].part_name == "ChildA"
    assert "extra" in derived.parts
    assert len(derived.connections) == 1
    c = derived.connections[0]
    assert (c.src_component, c.src_port, c.dst_component, c.dst_port) == (
        "right",
        "out_a",
        "extra",
        "in_b",
    )
    write_reference("inheritance_part_inheritance_add_replace_remove", architecture)


def test_part_inheritance_remove_connection_then_add_new_connection(tmp_path: Path):
    write_model(
        tmp_path / "model.sysml",
        """
        package Example {
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

          part def Derived : Base {
            remove connect a.out_signal to b.in_signal;
            connect a.out_signal to c.in_signal;
          }
        }
        """,
    )

    architecture = load_architecture(tmp_path)
    derived = architecture.part_definitions["Derived"]

    assert len(derived.connections) == 1
    c = derived.connections[0]
    assert (c.src_component, c.src_port, c.dst_component, c.dst_port) == (
        "a",
        "out_signal",
        "c",
        "in_signal",
    )
    write_reference(
        "inheritance_remove_connection_then_add_new_connection", architecture
    )
