# Grammars

This directory contains grammar files for the procedural_buildings engine.
Each file is a shape grammar that describes one or more building types.

## Showcase grammars (the ones to try first)

| Grammar | Start rule | Description |
|---|---|---|
| `orthodox_church` | `plot` | White church with green roof and golden dome |
| `soviet_block` | `plot` | Parametric panel block (gin-config) |
| `european_townhouse` | `plot` | Narrow 3-story urban townhouse |
| `medieval_house` | `plot` | Half-timbered facade |
| `material_building` | `plot` | Gin-configurable material/pattern system |
| `warehouse_district` | `block` | Industrial block with gabled/sawtooth roofs |
| `modern_district` | `district` | Glass tower + apartment + mixed-use |
| `site_layout` | `block` | Village block with khata + barn + tower |
| `facade_city` | `plot` | Multi-building city with adaptive facades |

## Feature demo grammars

| Grammar | Feature |
|---|---|
| `opening_demo` | Window/door openings in walls |
| `inset_demo` | Inset/decorative panels |
| `gin_demo` | Gin-config integration |
| `neighbor_facade` | Adaptive facade using env conditions |

## Op test grammars (`op_tests/`)

Each file in this directory exercises a single engine feature:
`split`, `repeat`, `repeatN`, `comp`, `colour`, `priority`,
`conditions`, `rand`, `randint`, `prim`, `params`, `constants`.

These are auto-discovered and run by `tests/test_op_grammars.py`.

## Archive (`_archive/`)

Historical/experimental grammars kept for reference. Not actively maintained.

## How to add a new grammar

1. Create a file in `grammars/<name>` (no extension).
2. The default start rule is `plot`. If your grammar needs a different
   one, add an entry to `GRAMMAR_OVERRIDES` in `tests/test_grammars.py`.
3. Run `pytest tests/test_grammars.py::test_grammar_renders` to verify.
4. For gin-controlled parameters, create a config in `configs/`.