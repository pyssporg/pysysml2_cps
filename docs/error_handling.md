# Error Handling

The parser raises explicit exceptions for structural issues.

## `FileNotFoundError`

- input folder does not exist
- no `*.sysml` files found in folder

## `KeyError`

- `load_system(..., system_part)` requested part does not exist

## `ValueError`

- missing package declaration
- mismatched package names across files
- duplicate definition names
- malformed declarations (`port`, `part`, `connect`, `redefines`, `remove`)
- unknown base definitions in `specializes`
- inheritance cycles
- invalid `redefines`/`remove` targets during inheritance merge
- inherited member collisions unless `redefines` is used
- unterminated `doc /* ... */` blocks
- unresolved `part` references to unknown part definitions
- unresolved `in/out port` references to unknown port definitions
- unresolved connection endpoint port definitions
- requirement usage outside `part def` / `port def`
- unresolved requirement references
