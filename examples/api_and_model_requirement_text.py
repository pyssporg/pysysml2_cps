from __future__ import annotations

from examples._example_helpers import parse_demo_architecture


def main() -> None:
    architecture = parse_demo_architecture()
    requirement = architecture.requirement_definitions["ReqA"]
    assert requirement.text == "Example requirement"


if __name__ == "__main__":
    main()
