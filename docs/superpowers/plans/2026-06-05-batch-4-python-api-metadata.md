# Batch 4: Python API + Grammar Metadata Implementation Plan

> **For agentic workers:** Use subagent-driven-development.

**Goal:** Importable BuildingGenerator class + structured metadata on all 17 showcase grammars.

**Architecture:** D1 and D2 are independent — dispatch in parallel.

---

### Task D1: BuildingGenerator class

**Files:**
- Create: `procedural_buildings/generator.py`
- Modify: `procedural_buildings/__init__.py`
- Test: verify GLB export + metadata parsing

- [ ] **Step 1: Create `procedural_buildings/generator.py`**

```python
import os
import random
import numpy as np
import gin
from .Processor import Processor
from .Scope import Scope
from . import materials


class BuildingGenerator:
    def __init__(
        self,
        grammar: str,
        seed: int | None = None,
        materials: str | None = None,
        params: dict | None = None,
        start_rule: str = "plot",
        start_scope: tuple = (0, 0, 0, 8, 8, 12),
    ):
        self.grammar_path = grammar
        self.start_rule = start_rule
        self.start_scope = Scope.freshScope(
            np.array(start_scope[:3]),
            np.array(start_scope[3:]),
        )
        self._metadata = self._parse_metadata()

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        gin_files = []
        gin_params = []
        if materials:
            gin_files.append(materials)
        if params:
            gin_params.append(f"grammar_var_overrides.values = {params}")
        gin.parse_config_files_and_bindings(gin_files, gin_params)

    def to_glb(self, path: str):
        p = Processor()
        p.grammarToGlb(self.grammar_path, self.start_rule, self.start_scope, path)

    def to_obj(self, path: str):
        p = Processor()
        p.grammarToManyObjs(
            self.grammar_path, self.start_rule, self.start_scope, 1, 0, path
        )

    def get_metadata(self) -> dict:
        return self._metadata

    def _parse_metadata(self) -> dict:
        meta = {"materials": [], "params": {}, "complexity": "unknown"}
        try:
            with open(self.grammar_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("# @meta"):
                        continue
                    if not line.startswith("# "):
                        break
                    content = line[2:].strip()
                    if content.startswith("materials:"):
                        meta["materials"] = [
                            m.strip() for m in content[10:].split(",")
                        ]
                    elif content.startswith("params:"):
                        for p in content[8:].split(","):
                            p = p.strip()
                            if "=" in p:
                                k, v = p.split("=", 1)
                                meta["params"][k.strip()] = v.strip()
                    elif content.startswith("complexity:"):
                        meta["complexity"] = content[11:].strip()
        except FileNotFoundError:
            pass
        return meta
```

- [ ] **Step 2: Update `procedural_buildings/__init__.py`**

```python
from .generator import BuildingGenerator
```

- [ ] **Step 3: Test**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config python -c "
from procedural_buildings import BuildingGenerator
gen = BuildingGenerator('grammars/orthodox_church', seed=42)
gen.to_glb('/tmp/api_test.glb')
meta = gen.get_metadata()
print('Metadata:', meta)
import os; print('GLB size:', os.path.getsize('/tmp/api_test.glb'))
"
```

- [ ] **Step 4: Commit**
```bash
git add procedural_buildings/generator.py procedural_buildings/__init__.py
git commit -m "feat: add BuildingGenerator class with to_glb/to_obj/get_metadata"
```

---

### Task D2: Grammar metadata

**Files:**
- Modify: all 17 showcase grammars in `grammars/`
- Test: metadata parsing

- [ ] **Step 1: Add # @meta headers to showcase grammars**

For each grammar, add a `# @meta` block at the top (after any existing `#` lines, before variable declarations):

**orthodox_church:**
```grammar
# @meta
# materials: plaster, roof_tile, gold
# params:
# complexity: medium
```

**soviet_block:**
```grammar
# @meta
# materials: concrete, glass
# params: numFloors=5, floorHeight=3
# complexity: high
```

**european_townhouse:**
```grammar
# @meta
# materials: plaster, roof_tile
# params:
# complexity: medium
```

**medieval_house:**
```grammar
# @meta
# materials: timber, plaster, roof_tile
# params:
# complexity: medium
```

**material_building:**
```grammar
# @meta
# materials: (gin-configured)
# params: wallPattern=0
# complexity: medium
```

**warehouse_district:**
```grammar
# @meta
# materials: brick, roof_tile, glass
# params: wallHeight=8, roofPitch=0.5
# complexity: high
```

**modern_district:**
```grammar
# @meta
# materials: glass, metal, plaster
# params:
# complexity: high
```

**site_layout:**
```grammar
# @meta
# materials: plaster, roof_tile, brick
# params:
# complexity: high
```

**facade_city:**
```grammar
# @meta
# materials: plaster, roof_tile
# params:
# complexity: high
```

**castle:**
```grammar
# @meta
# materials: stone, roof_tile
# params: keepHeight=12, towerHeight=8
# complexity: high
```

**bridge:**
```grammar
# @meta
# materials: stone
# params: span=12, pillarW=2
# complexity: low
```

**colored_city, city, gin_demo, inset_demo, neighbor_facade, opening_demo:**
Similar annotations based on what each grammar uses.

- [ ] **Step 2: Verify metadata parsing**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config python -c "
from procedural_buildings import BuildingGenerator
grammars = ['orthodox_church', 'soviet_block', 'european_townhouse', 'medieval_house',
            'material_building', 'warehouse_district', 'modern_district', 'site_layout',
            'castle', 'bridge', 'colored_city', 'city', 'gin_demo', 'inset_demo',
            'neighbor_facade', 'opening_demo', 'facade_city']
for g in grammars:
    gen = BuildingGenerator(f'grammars/{g}')
    meta = gen.get_metadata()
    print(f'{g}: materials={meta[\"materials\"]}, params={list(meta[\"params\"].keys())}, complexity={meta[\"complexity\"]}')
"
```

Expected: all grammars show metadata, none show "unknown".

- [ ] **Step 3: Run full tests**

```bash
cd /Users/vincent/Work/procedural-buildings
ruff format grammars/
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/ -q 2>&1 | tail -5
```

Commit:
```bash
git add grammars/
git commit -m "feat: add structured # @meta metadata to all showcase grammars"
```