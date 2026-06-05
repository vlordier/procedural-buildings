# Procedural Buildings

A shape-grammar engine for procedural generation of 3D building models.
Grammars describe buildings as nested splits, repeats, transforms, and
colours. Output is standard .obj format, viewable with any 3D viewer.

## Quick start

```bash
# Install dependencies
uv sync

# Render a grammar to .obj
uv run --with sly --with numpy --with sympy --with gin-config python -m procedural_buildings \
  -i grammars/material_building \
  -o outputs/example.obj \
  -s 0,0,0,8,8,12

# View it
uv run --with sly --with numpy --with sympy --with gin-config python -m procedural_buildings.view outputs/example.obj

# Validate a grammar (no output file needed)
uv run --with sly --with numpy --with sympy --with gin-config python -m procedural_buildings \
  --validate -i grammars/orthodox_church

# Reproducible build with a seed
uv run --with sly --with numpy --with sympy --with gin-config python -m procedural_buildings \
  -i grammars/modern_district \
  -o outputs/district.obj \
  -s 0,0,0,40,10,30 --seed 42
```

## Showcase grammars

| Grammar | Start rule | Example command |
|---|---|---|
| `orthodox_church` | `plot` | `-i grammars/orthodox_church -s 0,0,0,8,8,14` |
| `soviet_block` | `plot` | `-i grammars/soviet_block -s 0,0,0,12,8,15` |
| `european_townhouse` | `plot` | `-i grammars/european_townhouse -s 0,0,0,8,8,12` |
| `medieval_house` | `plot` | `-i grammars/medieval_house -s 0,0,0,10,8,10` |
| `material_building` | `plot` | `-i grammars/material_building -s 0,0,0,8,8,12` |
| `warehouse_district` | `block` | `-i grammars/warehouse_district -s 0,0,0,40,10,20` |
| `modern_district` | `district` | `-i grammars/modern_district -s 0,0,0,40,10,30` |
| `site_layout` | `block` | `-i grammars/site_layout -s 0,0,0,40,10,20` |

## Gin-config integration

Grammar parameters can be overridden at runtime:

```bash
uv run --with sly --with numpy --with sympy --with gin-config python -m procedural_buildings \
  -i grammars/material_building \
  -o outputs/checker.obj \
  -s 0,0,0,8,8,12 \
  -g configs/checker.gin
```

See `configs/README.md` for available configs and how to write new ones.

## CLI reference

```
-i <grammar_file>       Input grammar
-o <output.obj>         Output .obj file
-s <x1,y1,z1,x2,y2,z2>  Start scope (default 0,0,0,8,8,12)
-R <rule>                Start rule (default "plot")
--seed <N>               Reproducible random seed
--validate               Parse + simplify only, no output
-g <config.gin>          Gin config file
-p <bindings>            Gin inline bindings
-r                       Reverse path: .obj → grammar
-n <count>               Number of buildings (for multi-building)
-d <distance>             Separation between buildings
-f                       One .obj file per building
-v                       Verbose logging
```

## Running tests

```bash
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/
```

## Project structure

- `procedural_buildings/` — Engine source (Ops, Scope, Lexer, Parser, Processor, etc.)
- `grammars/` — Shape grammar files (see grammars/README.md)
- `configs/` — Gin-config parameter files (see configs/README.md)
- `tests/` — Pytest test suite
- `primitives/` — Primitive .obj files (rect, triangle, dome, etc.)
- `scripts/` — Utility scripts (update golden hashes, .obj → .glb)
- `docs/` — Documentation

## License

MIT