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
from pycps_sysmlv2 import load_architecture, export_architecture
```

Main entrypoint:
- `load_architecture(path)`:
  - If `path` is a folder, parses all `*.sysml` files in that folder.
  - If `path` is a file, parses only that file.
  - Returns a `SysMLArchitecture` object with:
    - `package`
    - `part_definitions`
    - `port_definitions`
    - `requirements`
- `export_architecture(architecture, mode="declared" | "flattened")`:
  - Emits SysML text from the in-memory architecture.
- `export_architecture_files(architecture, mode="declared")`:
  - Emits a `dict[file_name, sysml_text]` grouped by original source file when known.

## Quickstart

[Example](examples/parse_architecture.py)

```python
from pycps_sysmlv2 import load_architecture

architecture = load_architecture("tests/fixtures/fixture_a")
fixture = architecture.part_definitions["FixtureAComposition"]

# Connections belong to the part definition, not SysMLArchitecture.
for connection in fixture.connections:
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

Given a target path, the parser:
1. Reads the target `*.sysml` file, or all `*.sysml` files in a target directory, and checks they share the same `package`.
2. Extracts:
   - `part def ... { ... }`
   - `port def ... { ... }`
   - `requirement def ... { ... }` and `requirement ... : ...;`
3. Parses members inside `part def` / `port def` blocks:
   - `attribute ...`
   - `in port ...` / `out port ...`
   - `part instance : PartDefinition;`
   - `connect A.port to B.port;`
   - inheritance mutation statements (`redefines ...`, `remove ...`)
4. Resolves cross-links:
  - Part inheritance (merge order: remove -> redefines -> add)
   - Port references -> port definitions
   - Part instances -> part definitions
   - Connections -> source/destination part and port references

Output is a connected Python object graph (not raw text tokens), so downstream logic can
operate directly on resolved objects.

## Supported SysML subset

The parser currently supports:
- `package Name { ... }`
- `part def Name { ... }`
- `part def Derived specializes Base { ... }`
- `port def Name { ... }`
- `attribute x = <literal>;`
- `attribute x: <type>;`
- `in port p : PortType;`
- `out port p : PortType;`
- `part child : PartDef;`
- `connect srcPart.srcPort to dstPart.dstPort;`
- `redefines attribute x = <literal>;`
- `redefines in port p : PortType;` / `redefines out port p : PortType;`
- `redefines part child : PartDef;`
- `remove attribute x;`
- `remove port p;`
- `remove part child;`
- `remove connect srcPart.srcPort to dstPart.dstPort;`
- `doc /* ... */` comments on parts/ports/attributes/references
- `requirement def RequirementName { doc /* ... */ }`
- `requirement ReqId : RequirementName;`

Literal parsing:
- Booleans (`true`/`false`), numbers, strings, lists, and other Python-literal-compatible
  values via `ast.literal_eval`
- This parser does not evaluate full SysML expression semantics (for example, units-aware expressions).

## Subset vs Extension

- Supported SysML v2-style subset:
  - `specializes` for part inheritance
  - `redefines` for overriding inherited members
  - `requirement def` and `requirement` usage extraction
- Project-specific extension:
  - `remove ...` mutation statements

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
arch = load_architecture("tests/fixtures/fixture_a")

# File input parses only that file
arch = load_architecture("tests/fixtures/fixture_a/composition.sysml")

print(arch.package)  # FixtureA
print(len(arch.part_definitions), "part definitions")
print(len(arch.port_definitions), "port definitions")
```

### 2. Inspect a component interface contract (ports + typed attributes)

```python
from pycps_sysmlv2 import load_architecture

arch = load_architecture("tests/fixtures/fixture_a")
child_a = arch.part_definitions["ChildA"]

for port_name, port_ref in child_a.ports.items():
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

arch = load_architecture("tests/fixtures/fixture_a")
for req in arch.requirements:
    print(req.identifier, "->", req.text)
```

### 4. Detect unresolved wiring in connections

```python
from pycps_sysmlv2 import load_architecture

arch = load_architecture("tests/fixtures/fixture_a")
top = arch.part_definitions["FixtureAComposition"]

for c in top.connections:
    is_resolved = all([c.src_part_def, c.dst_part_def, c.src_port_def, c.dst_port_def])
    if not is_resolved:
        print("UNRESOLVED:", c.src_component, c.src_port, "->", c.dst_component, c.dst_port)
```

### 5. Read parsed attributes as Python literals

```python
from pycps_sysmlv2 import load_architecture

arch = load_architecture("tests/fixtures/fixture_a")
child_a = arch.part_definitions["ChildA"]

print(child_a.attributes["countA"].value)   # 3 (int)
print(child_a.attributes["valuesA"].value)  # [1.0, 2.0, 3.0] (list[float])
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
  - malformed `port`, `part`, `connect`, `redefines`, or `remove` statements
  - unknown base parts in `part def Derived specializes Base { ... }`
  - inheritance cycles
  - invalid `redefines`/`remove` targets during inheritance merge
  - inherited member collisions unless `redefines` is used
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
- `src/pycps_sysmlv2/inheritance.py` - inheritance merge pass
- `src/pycps_sysmlv2/exporter.py` - SysML text export
- `tests/` - package-local tests
- `examples/` - small usage scripts
- `docs/` - package-specific notes

Package tests use generic fixtures under `tests/fixtures/fixture_a/` and
`tests/fixtures/fixture_b/` so validation stays small and easy to verify.
