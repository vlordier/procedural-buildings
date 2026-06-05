# Batch 5: Batch Generation Implementation Plan

**Files:**
- Modify: `procedural_buildings/generator.py`

- [ ] **Step 1: Read current generator.py**

```bash
cd /Users/vincent/Work/procedural-buildings
cat procedural_buildings/generator.py
```

- [ ] **Step 2: Add GRAMMAR_LIBRARY and new methods**

Add before the class:
```python
SHOWCASE_GRAMMARS = [
    {"name": "orthodox_church", "path": "grammars/orthodox_church",
     "materials": ["plaster", "roof_tile", "gold"], "complexity": "medium",
     "params": {}, "start_rule": "plot", "start_scope": (0, 0, 0, 8, 8, 14)},
    {"name": "soviet_block", "path": "grammars/soviet_block",
     "materials": ["concrete", "glass"], "complexity": "high",
     "params": {"numFloors": 5, "floorHeight": 3},
     "start_rule": "plot", "start_scope": (0, 0, 0, 12, 8, 15)},
    {"name": "european_townhouse", "path": "grammars/european_townhouse",
     "materials": ["plaster", "roof_tile"], "complexity": "medium",
     "params": {}, "start_rule": "plot", "start_scope": (0, 0, 0, 8, 8, 12)},
    {"name": "medieval_house", "path": "grammars/medieval_house",
     "materials": ["timber", "plaster", "roof_tile"], "complexity": "medium",
     "params": {}, "start_rule": "plot", "start_scope": (0, 0, 0, 10, 8, 10)},
    {"name": "warehouse_district", "path": "grammars/warehouse_district",
     "materials": ["brick", "roof_tile", "glass"], "complexity": "high",
     "params": {}, "start_rule": "block", "start_scope": (0, 0, 0, 40, 10, 20)},
    {"name": "modern_district", "path": "grammars/modern_district",
     "materials": ["glass", "metal", "plaster"], "complexity": "high",
     "params": {}, "start_rule": "district", "start_scope": (0, 0, 0, 40, 10, 30)},
    {"name": "castle", "path": "grammars/castle",
     "materials": ["stone", "roof_tile"], "complexity": "high",
     "params": {"keepHeight": 12, "towerHeight": 8},
     "start_rule": "plot", "start_scope": (0, 0, 0, 20, 20, 20)},
    {"name": "bridge", "path": "grammars/bridge",
     "materials": ["stone"], "complexity": "low",
     "params": {"span": 12, "pillarW": 2},
     "start_rule": "plot", "start_scope": (0, 0, 0, 16, 4, 8)},
    {"name": "gin_demo", "path": "grammars/gin_demo",
     "materials": ["(gin-configured)"], "complexity": "medium",
     "params": {"panelR": 0.75}, "start_rule": "plot",
     "start_scope": (0, 0, 0, 8, 8, 12)},
    {"name": "inset_demo", "path": "grammars/inset_demo",
     "materials": ["plaster"], "complexity": "low",
     "params": {}, "start_rule": "plot", "start_scope": (0, 0, 0, 8, 8, 12)},
    {"name": "neighbor_facade", "path": "grammars/neighbor_facade",
     "materials": ["plaster", "roof_tile"], "complexity": "medium",
     "params": {}, "start_rule": "plot", "start_scope": (0, 0, 0, 8, 8, 12)},
    {"name": "opening_demo", "path": "grammars/opening_demo",
     "materials": ["plaster", "glass"], "complexity": "medium",
     "params": {}, "start_rule": "plot", "start_scope": (0, 0, 0, 8, 8, 12)},
]
```

Add class methods to `BuildingGenerator`:

```python
@classmethod
def library(cls):
    return list(SHOWCASE_GRAMMARS)

@classmethod
def random(cls, seed=None, complexity=None, materials=None, params=None):
    import random as _random
    candidates = SHOWCASE_GRAMMARS
    if complexity:
        candidates = [g for g in candidates if g["complexity"] == complexity]
    if not candidates:
        candidates = SHOWCASE_GRAMMARS
    choice = _random.Random(seed).choice(candidates)
    return cls(
        grammar=choice["path"],
        seed=seed,
        materials=materials,
        params={**choice.get("params", {}), **(params or {})},
        start_rule=choice.get("start_rule", "plot"),
        start_scope=choice.get("start_scope", (0, 0, 0, 8, 8, 12)),
    )

@classmethod
def batch(cls, count, seed_start=0, materials=None, params=None,
          output_dir="buildings"):
    import os
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    for i in range(count):
        gen = cls.random(seed=seed_start + i, materials=materials, params=params)
        path = os.path.join(output_dir, f"building_{seed_start + i:04d}.glb")
        gen.to_glb(path)
        paths.append(path)
    return paths
```

- [ ] **Step 3: Test**

```bash
cd /Users/vincent/Work/procedural-buildings
ruff check --fix procedural_buildings/ && ruff format procedural_buildings/
uv run --with sly --with numpy --with sympy --with gin-config python -c "
from procedural_buildings import BuildingGenerator

# Library
lib = BuildingGenerator.library()
print(f'Library: {len(lib)} grammars')

# Random gen
g = BuildingGenerator.random(seed=42)
m = g.get_metadata()
print(f'Random: {g.grammar_path} -> {m[\"materials\"]}')

# Batch
paths = BuildingGenerator.batch(3, seed_start=0, output_dir='/tmp/batch_test/')
import os
print(f'Batch: {len(paths)} files, {os.path.getsize(paths[0])} bytes each')
"
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/ -q 2>&1 | tail -5
```

- [ ] **Step 4: Commit**

```bash
git add procedural_buildings/generator.py
git commit -m "feat: add random(), batch(), library() to BuildingGenerator"
```