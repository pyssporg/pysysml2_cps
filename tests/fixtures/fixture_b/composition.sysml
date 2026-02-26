package FixtureB {
  part def FixtureBBase {
    attribute removeA = 1;
    attribute replaceA = 10;
    in port removePortA : SignalA;
    out port replacePortA : SignalA;
    part leftA : ChildA;
    part rightB : ChildB;
    connect leftA.outA to rightB.inA;
  }

  part def FixtureB : FixtureBBase {
    remove attribute removeA;
    remove port removePortA;
    remove connect leftA.outA to rightB.inA;

    replace attribute replaceA = 99;
    replace out port replacePortA : SignalB;
    replace part rightB : ChildA;

    attribute addA = true;
    in port addPortA : SignalA;
    part extraB : ChildB;
    connect rightB.outA to extraB.inA;
  }
}
