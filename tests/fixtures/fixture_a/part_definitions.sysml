package FixtureA {
  part def ChildA {
    attribute countA = 3;
    attribute valuesA = [1.0, 2.0, 3.0];
    in port inA : SignalA;
    out port outB : SignalB;
  }

  part def ChildB {
    in port inB : SignalB;
  }

  part def ChildC {
    out port outA : SignalA;
  }
}
