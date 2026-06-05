# Batch 5: Batch Generation + Random Selection — Spec

**Goal:** `BuildingGenerator.random()` and `BuildingGenerator.batch()` for
populating scenes with many buildings.

## New methods on BuildingGenerator

### `@classmethod BuildingGenerator.random(seed, complexity=None, materials=None, params=None)`
Picks a random grammar from the library. Filters by complexity if given.

```python
gen = BuildingGenerator.random(seed=42)
gen.to_glb("building.glb")

gen = BuildingGenerator.random(seed=42, complexity="medium")
```

### `@classmethod BuildingGenerator.batch(count, seed_start=0, materials=None, output_dir="buildings/")`
Generates `count` buildings with sequential seeds, writes to output_dir.

```python
BuildingGenerator.batch(10, seed_start=0, output_dir="city/")
# Writes city/building_0000.glb, city/building_0001.glb, ...
```

### `@classmethod BuildingGenerator.library()`
Returns list of all showcase grammars with their metadata.

```python
for g in BuildingGenerator.library():
    print(g["name"], g["materials"], g["complexity"])
```

## Grammar library registry

A list in `generator.py` defining all showcase grammars:

```python
GRAMMAR_LIBRARY = [
    {"name": "orthodox_church", "path": "grammars/orthodox_church", "complexity": "medium"},
    {"name": "castle", "path": "grammars/castle", "complexity": "high"},
    ...
]
```

## Files
- Modify: `procedural_buildings/generator.py`

## Acceptance
```python
from procedural_buildings import BuildingGenerator

g = BuildingGenerator.random(seed=42)
assert "materials" in g.get_metadata()

lib = BuildingGenerator.library()
assert len(lib) >= 17

BuildingGenerator.batch(5, seed_start=0, output_dir="/tmp/buildings/")
import os
assert len(os.listdir("/tmp/buildings/")) == 5
```