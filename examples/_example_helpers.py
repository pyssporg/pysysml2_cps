from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from pycps_sysmlv2 import SysMLParser


DEMO_MODEL = """
package Example {
  requirement def ReqA {
    doc /* Example requirement */
  }

  port def Signal {
    requirement signal_req : ReqA;
  }

  part def Source {
    attribute gain = 2;
    out port out_signal : Signal;
  }

  part def Sink {
    in port in_signal : Signal;
  }

  part def System {
    part src : Source;
    part dst : Sink;
    requirement system_req : ReqA;
    connect src.out_signal to dst.in_signal;
  }
}
""".strip()


def write_demo_model(root: Path) -> Path:
    model_path = root / "model.sysml"
    model_path.write_text(DEMO_MODEL + "\n")
    return model_path


def parse_demo_architecture():
    with TemporaryDirectory() as tmp:
        model_path = write_demo_model(Path(tmp))
        return SysMLParser(model_path).parse()
