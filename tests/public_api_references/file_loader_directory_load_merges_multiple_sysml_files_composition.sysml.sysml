package Example {
  part def System {
    part dst : Consumer;
    part src : Producer;
    connect src.out_signal to dst.in_signal;
  }
}
