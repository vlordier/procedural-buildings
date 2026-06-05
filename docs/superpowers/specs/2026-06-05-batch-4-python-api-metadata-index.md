# Batch 4: Python API + Grammar Metadata — Index

**Goal:** Make the project importable as a Python library with a clean
`BuildingGenerator` class, and add structured metadata to all showcase
grammars.

| # | Item | Files | Effort |
|---|---|---|---|
| D1 | BuildingGenerator class | Create: `procedural_buildings/generator.py`; Modify: `procedural_buildings/__init__.py` | Medium |
| D2 | Grammar metadata | Modify: all 17 showcase grammars; `tests/test_metadata.py` | Medium |

Both items are independent and can be done in parallel.

## Acceptance

- `from procedural_buildings import BuildingGenerator` works
- `BuildingGenerator(grammar="castle", seed=42).to_glb("out.glb")` produces a valid GLB
- `BuildingGenerator(grammar="castle").get_metadata()` returns materials, params, complexity
- All showcase grammars have `# @meta` headers
- `pytest tests/` passes