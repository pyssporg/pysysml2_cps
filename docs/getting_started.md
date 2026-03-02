# Getting Started

## Requirements

- Python 3.10 or newer

## Install

From the repository root:

```bash
pip install -e .
```

Or as a regular package install:

```bash
pip install .
```

Install directly from GitHub:

```bash
pip install "git+https://github.com/jkCXf9X4/py_sysml_v2_cps.git"
```

Pin to a branch or tag:

```bash
pip install "git+https://github.com/jkCXf9X4/py_sysml_v2_cps.git@main"
pip install "git+https://github.com/jkCXf9X4/py_sysml_v2_cps.git@v0.1.0"
```

## First Load

```python
from pycps_sysmlv2 import SysMLParser

architecture = SysMLParser("tests/fixtures/fixture_a").parse()
print(architecture.package)
print(len(architecture.part_definitions), "part definitions")
print(len(architecture.port_definitions), "port definitions")
print(len(architecture.requirement_definitions), "requirement definitions")
```

## Common Use Cases

### 1. Load architecture from folder or single file

```python
from pycps_sysmlv2 import SysMLParser

# Folder input: all *.sysml files
arch = SysMLParser("tests/fixtures/fixture_a").parse()

# File input: only that file
arch = SysMLParser("tests/fixtures/fixture_a/composition.sysml").parse()
```

### 2. Inspect ports and typed attributes

```python
from pycps_sysmlv2 import SysMLParser

arch = SysMLParser("tests/fixtures/fixture_a").parse()
child = arch.part_definitions["ChildA"]

for port_name, port_ref in child.ports.items():
    print(port_ref.direction, port_name, "->", port_ref.port_name)
    if port_ref.port_def:
        for attr in port_ref.port_def.attributes.values():
            print("  -", attr.name, ":", attr.type.as_string())
```

### 3. Trace requirement references

```python
from pycps_sysmlv2 import SysMLParser

arch = SysMLParser("tests/fixtures/fixture_a").parse()
for req_name, req_ref in arch.part_definitions["FixtureAComposition"].items["requirements"].items():
    print(req_name, "->", req_ref.requirement_name, "->", req_ref.text)
```

### 4. Walk resolved connections

```python
from pycps_sysmlv2 import SysMLParser

arch = SysMLParser("tests/fixtures/fixture_a").parse()
top = arch.part_definitions["FixtureAComposition"]

for c in top.connections:
    print(
        c.src_part_def.name,
        c.src_port_def.name,
        "->",
        c.dst_part_def.name,
        c.dst_port_def.name,
    )
```

### 5. Export SysML

```python
from pycps_sysmlv2 import SysMLParser

arch = SysMLParser("tests/fixtures/fixture_a").parse()
print(arch.export_flattened())

files = arch.export_declared()
for name, text in files.items():
    print(name, len(text))
```
