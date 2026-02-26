# Test Fixtures

Fixtures are split into small generic cases for easier verification:

- `fixture_a/`: baseline parsing and link-resolution coverage
- `fixture_b/`: inheritance coverage (`add`, `replace`, `remove`)

Each fixture folder contains separate `*.sysml` files to exercise folder-level
loading and merge behavior.

- `part def` blocks with attributes and in/out ports
- `port def` payload schemas
- `connect` statements
- `comment` requirement entries
