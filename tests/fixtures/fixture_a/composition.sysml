package FixtureA {
  part def FixtureAComposition {
    part leftA : ChildA;
    part rightB : ChildB;
    part sourceC : ChildC;

    connect leftA.outB to rightB.inB;
    connect sourceC.outA to leftA.inA;
  }
}
