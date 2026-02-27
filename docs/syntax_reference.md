# SysML Subset Reference

## Overview

`pycps_sysmlv2` implements a practical subset of SysML v2 for architecture parsing.

## Supported Declarations

- `package Name { ... }`
- `part def Name { ... }`
- `part def Derived specializes Base { ... }`
- `port def Name { ... }`
- `port def DerivedPort specializes BasePort { ... }`
- `requirement def RequirementName { ... }`
- `requirement def ChildRequirement specializes ParentRequirement { ... }`

## Supported Members in `part def` / `port def`

- `attribute x = <literal>;`
- `attribute x: <type>;`
- `in port p : PortType;`
- `out port p : PortType;`
- `part child : PartDef;`
- `requirement ReqId : RequirementDef;`
- `connect srcPart.srcPort to dstPart.dstPort;`

## Inheritance Mutation Statements

- `redefines attribute x = <literal>;`
- `redefines in port p : PortType;`
- `redefines out port p : PortType;`
- `redefines part child : PartDef;`
- `redefines requirement ReqId : RequirementDef;`
- `remove attribute x;`
- `remove port p;`
- `remove part child;`
- `remove requirement ReqId;`
- `remove connect srcPart.srcPort to dstPart.dstPort;`

## Requirement Handling

- Requirement definitions are declared at top level using `requirement def`.
- Requirement usages are references that must appear inside `part def` or `port def` blocks.
- Top-level `requirement ...;` usage is rejected.

## Comments

- `doc /* ... */` comments are supported on definitions and members.

## Primitive Type Normalization

- Real: `Real`, `float`, `float32`, `float64`, `double`
- Integer: `Integer`, `int`, `int8`, `int32`, `uint8`, `uint32`
- Boolean: `Boolean`, `bool`
- String: `String`

## Literal Parsing

Values are parsed via Python literal semantics (`ast.literal_eval`):

- booleans (`true`/`false`)
- numbers
- strings
- lists

Non-goal: full SysML expression semantics (for example, units-aware expressions).
