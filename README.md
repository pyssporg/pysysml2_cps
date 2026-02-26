# pycps_sysmlv2

Standalone Python SysML v2 parsing and helper utilities for CPS development.

## What this module does

`pycps_sysmlv2` parses a folder of lightweight SysML v2 text files (`*.sysml`) into a
single in-memory architecture model you can inspect from Python.

It is designed for:
- Loading component architectures into scripts/tests
- Inspecting parts, ports, attributes, and requirements
- Following wiring (`connect ... to ...`) with resolved links to component/port definitions
- Building validation/reporting tooling on top of parsed model objects

It is not a full SysML v2 compiler. It targets a practical subset used in this repository.

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

Install directly from GitHub (no separate manual build step):

```bash
pip install "git+https://github.com/jkCXf9X4/py_sysml_v2_cps.git"
```

Pin to a branch or tag:

```bash
pip install "git+https://github.com/jkCXf9X4/py_sysml_v2_cps.git@main"
pip install "git+https://github.com/jkCXf9X4/py_sysml_v2_cps.git@v0.1.0"
```

## Public API

Main import:

```python
from pycps_sysmlv2 import load_architecture
```

Main entrypoint:
- `load_architecture(path)`:
  - If `path` is a folder, parses all `*.sysml` files in that folder.
  - If `path` is a file, parses the file's parent folder.
  - Returns a `SysMLArchitecture` object with:
    - `package`
    - `part_definitions`
    - `port_definitions`
    - `requirements`

## Quickstart

[Example](examples/parse_architecture.py)

```python
from pycps_sysmlv2 import load_architecture

architecture = load_architecture("tests/fixtures/aircraft_subset")
aircraft = architecture.part_definitions["AircraftComposition"]

# Connections belong to the part definition, not SysMLArchitecture.
for connection in aircraft.connections:
    print(
        connection.src_part_def.name,
        connection.src_port_def.name,
        "->",
        connection.dst_part_def.name,
        connection.dst_port_def.name,
    )
```

Run the bundled example from this repository root:

```bash
PYTHONPATH=src python3 examples/parse_architecture.py
```

## Architecture transparency

Development-facing architecture and design details are documented in:

- [`docs/architecture_overview.md`](docs/architecture_overview.md)

It includes:
- Parsing pipeline and module responsibilities
- Data model and reference-resolution strategy
- Validation/error behavior and failure taxonomy
- Extension points for adding syntax, validation, and diagnostics

## How parsing works

Given a target directory, the parser:
1. Reads all `*.sysml` files and checks they share the same `package`.
2. Extracts:
   - `part def ... { ... }`
   - `port def ... { ... }`
   - `comment Requirement_* /* ... */` style requirements
3. Parses members inside `part def` / `port def` blocks:
   - `attribute ...`
   - `in port ...` / `out port ...`
   - `part instance : PartDefinition;`
   - `connect A.port to B.port;`
   - inheritance mutation statements (`replace ...`, `remove ...`)
4. Resolves cross-links:
   - Part inheritance (merge order: remove -> replace -> add)
   - Port references -> port definitions
   - Part instances -> part definitions
   - Connections -> source/destination part and port references

Output is a connected Python object graph (not raw text tokens), so downstream logic can
operate directly on resolved objects.

## Supported SysML subset

The parser currently supports:
- `package Name { ... }`
- `part def Name { ... }`
- `part def Derived : Base { ... }`
- `port def Name { ... }`
- `attribute x = <literal>;`
- `attribute x: <type>;`
- `in port p : PortType;`
- `out port p : PortType;`
- `part child : PartDef;`
- `connect srcPart.srcPort to dstPart.dstPort;`
- `replace attribute x = <literal>;`
- `replace in port p : PortType;` / `replace out port p : PortType;`
- `replace part child : PartDef;`
- `remove attribute x;`
- `remove port p;`
- `remove part child;`
- `remove connect srcPart.srcPort to dstPart.dstPort;`
- `doc /* ... */` comments on parts/ports/attributes/references
- `comment Requirement_ID /* ... */` requirement extraction

Literal parsing:
- Booleans (`true`/`false`), numbers, strings, lists, and other Python-literal-compatible
  values via `ast.literal_eval`

Primitive type normalization includes common aliases:
- Real: `Real`, `float`, `float32`, `float64`, `double`
- Integer: `Integer`, `int`, `int8`, `int32`, `uint8`, `uint32`
- Boolean: `Boolean`, `bool`
- String: `String`

## Common use cases

### 1. Load an architecture from a folder or a single `.sysml` file

```python
from pycps_sysmlv2 import load_architecture

# Folder input (all *.sysml files in the directory are parsed)
arch = load_architecture("tests/fixtures/aircraft_subset")

# File input also works (the file's parent folder is parsed)
arch = load_architecture("tests/fixtures/aircraft_subset/composition.sysml")

print(arch.package)  # Aircraft
print(len(arch.part_definitions), "part definitions")
print(len(arch.port_definitions), "port definitions")
```

### 2. Inspect a component interface contract (ports + typed attributes)

```python
from pycps_sysmlv2 import load_architecture

arch = load_architecture("tests/fixtures/aircraft_subset")
autopilot = arch.part_definitions["AutopilotModule"]

for port_name, port_ref in autopilot.ports.items():
    direction = port_ref.direction
    target = port_ref.port_name
    print(f"{direction} {port_name}: {target}")

    if port_ref.port_def:
        for attr in port_ref.port_def.attributes.values():
            print("  -", attr.name, ":", attr.type.as_string())
```

### 3. Trace parsed requirements for downstream checks/reporting

```python
from pycps_sysmlv2 import load_architecture

arch = load_architecture("tests/fixtures/aircraft_subset")
for req in arch.requirements:
    print(req.identifier, "->", req.text)
```

### 4. Detect unresolved wiring in connections

```python
from pycps_sysmlv2 import load_architecture

arch = load_architecture("tests/fixtures/aircraft_subset")
top = arch.part_definitions["AircraftComposition"]

for c in top.connections:
    is_resolved = all([c.src_part_def, c.dst_part_def, c.src_port_def, c.dst_port_def])
    if not is_resolved:
        print("UNRESOLVED:", c.src_component, c.src_port, "->", c.dst_component, c.dst_port)
```

### 5. Read parsed attributes as Python literals

```python
from pycps_sysmlv2 import load_architecture

arch = load_architecture("tests/fixtures/aircraft_subset")
autopilot = arch.part_definitions["AutopilotModule"]

print(autopilot.attributes["waypointCount"].value)   # 10 (int)
print(autopilot.attributes["waypointX_km"].value)    # [0.0, 10.0, 20.0] (list[float])
print(autopilot.attributes["comment"].value)         # "uses waypoint tracking" (str)
```

## Data model overview

Core classes (in `src/pycps_sysmlv2/definitions.py`):
- `SysMLArchitecture`: top-level package + collected definitions
- `SysMLPartDefinition`: attributes, ports, subparts, connections
- `SysMLPortDefinition`: typed payload attributes
- `SysMLConnection`: parsed connect statement + resolved src/dst links
- `SysMLRequirement`: requirement identifier + text
- `SysMLPartReference` and `SysMLPortReference`: instance/reference nodes with resolved targets

## Error behavior and constraints

The parser raises explicit exceptions for common structural issues:
- `FileNotFoundError`:
  - input folder does not exist
  - no `*.sysml` files found in folder
- `KeyError`:
  - `load_system(..., system_part)` requested part does not exist
- `ValueError`:
  - missing package declaration
  - mismatched package names across files
  - duplicate `part def` or `port def` names
  - malformed `port`, `part`, `connect`, `replace`, or `remove` statements
  - unknown base parts in `part def Derived : Base { ... }`
  - inheritance cycles
  - invalid `replace`/`remove` targets during inheritance merge
  - inherited member collisions unless `replace` is used
  - unterminated `doc /* ... */` comment blocks
  - unresolved `part` references to unknown part definitions
  - unresolved `in/out port` references to unknown port definitions
  - unresolved connection endpoint port definitions

## Scope and non-goals

This package is intentionally lightweight and currently does not attempt to support:
- Full SysML v2 language coverage
- Constraint/equation solving
- Behavioral semantics/state machines
- Model transformation or code generation pipelines

## Development

Run package-local tests:

```bash
python3.11 -m venv venv && . venv/bin/activate && pip install -r requirements.txt
```

```bash
python -m pytest -q
```

Build distributable artifacts:

```bash
python -m build
```

## Package layout

- `src/pycps_sysmlv2/` - package implementation
- `tests/` - package-local tests
- `examples/` - small usage scripts
- `docs/` - package-specific notes

Package tests use `tests/fixtures/aircraft_subset/`, a compact subset extracted
from the original project architecture so validation is self-contained.
