from pathlib import Path
import runpy
import sys


EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"
REPO_ROOT = EXAMPLES_DIR.parent


def test_documentation_examples_run_without_errors():
    """Keep runnable documentation examples exercised by the test suite."""
    sys.path.insert(0, str(REPO_ROOT))
    example_paths = sorted(
        path
        for path in EXAMPLES_DIR.glob("*.py")
        if not path.name.startswith("_")
    )

    assert example_paths

    for example_path in example_paths:
        runpy.run_path(str(example_path), run_name="__main__")
