# Cluster 1: Test Infrastructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add test infrastructure so the engine's correctness is verifiable: grammar smoke tests, CLI flags for reproducibility and validation, round-trip tests, golden snapshots.

**Architecture:** 6 independent items in 3 waves. Wave 1 (1.1, 1.2, 1.3) are fully parallel — no shared state. Wave 2 (1.4) reuses the test harness pattern from 1.1. Wave 3 (1.5, 1.6) depend on 1.2 for determinism. Each item produces one new test file and/or one CLI change in `__main__.py`.

**Tech Stack:** Python 3.12, pytest, existing procedural_buildings engine, Processor class, Scope, __main__.py

---

### Task 1.1: `tests/test_grammars.py` — auto-discover and render every grammar

**Files:**
- Create: `tests/test_grammars.py`

- [ ] **Step 1: Create `tests/test_grammars.py`**

Write the test file:

```python
import os
import pytest
import numpy as np
from procedural_buildings.Processor import Processor
from procedural_buildings.Scope import Scope

GRAMMARS_DIR = "grammars"
SKIP_DIRS = {"_archive", "op_tests", "__pycache__"}
START_SCOPE = Scope.freshScope(np.array([0, 0, 0]), np.array([8, 8, 12]))

GRAMMAR_OVERRIDES = {
    "grammars/site_layout": ("block", (0, 0, 0, 40, 10, 20)),
    "grammars/warehouse_district": ("block", (0, 0, 0, 40, 10, 20)),
    "grammars/modern_district": ("district", (0, 0, 0, 40, 10, 30)),
}

XFAIL_GRAMMARS = {
    "grammars/foo",
    "grammars/window",
    "grammars/cabin",
    "grammars/overlap",
}

def _discover_grammars():
    for entry in sorted(os.listdir(GRAMMARS_DIR)):
        path = os.path.join(GRAMMARS_DIR, entry)
        if not os.path.isfile(path):
            continue
        if entry.startswith("."):
            continue
        yield path

@pytest.mark.parametrize("grammar_path", list(_discover_grammars()))
def test_grammar_renders(grammar_path, tmp_path):
    filename = os.path.basename(grammar_path)
    if filename in XFAIL_GRAMMARS:
        pytest.xfail("Known-broken scratch grammar, will be deleted in cluster 3")

    override = GRAMMAR_OVERRIDES.get(grammar_path)
    if override:
        start_rule, scope_coords = override
        start_scope = Scope.freshScope(np.array(scope_coords[:3]), np.array(scope_coords[3:]))
    else:
        start_rule = "plot"
        start_scope = START_SCOPE

    p = Processor()
    out_path = str(tmp_path / "out.obj")
    p.grammarToManyObjs(grammar_path, start_rule, start_scope, 1, 0, out_path)
    assert os.path.exists(out_path), f"No OBJ written for {grammar_path}"
    assert os.path.getsize(out_path) > 0, f"Empty OBJ for {grammar_path}"
```

- [ ] **Step 2: Run it**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/test_grammars.py -v 2>&1 | tail -60
```

Expected: All grammar files pass except the 4 xfail ones.

- [ ] **Step 3: Commit**

```bash
git add tests/test_grammars.py
git commit -m "test: add auto-discover grammar render tests"
```

---

### Task 1.2: `--seed` CLI flag

**Files:**
- Modify: `procedural_buildings/__main__.py`
- Test: use existing grammars

This is a small change. No separate test file needed — the golden test (1.6) will exercise it.

- [ ] **Step 1: Edit `__main__.py`**

Add `import random` at the top. Add `seed = None` to the local vars. Add `"seed="` to the long opts list. Add parsing:

After line 106 (`elif opt in ("-v", "--verbose"): ...`), add:
```python
        elif opt == "--seed":
            try:
                seed = int(arg)
            except ValueError:
                log.error("Error: --seed must be an integer")
                sys.exit(2)
```

After line 114 (`gin.parse_config_files_and_bindings(ginFiles, ginParams)`), add:
```python
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
```

Add `" [--seed <N>]"` to the usage string (line 36).

- [ ] **Step 2: Verify**

```bash
cd /Users/vincent/Work/procedural-buildings
python -m procedural_buildings -i grammars/modern_district -o /tmp/seeda.obj -s 0,0,0,40,10,30 --seed 42 2>&1
python -m procedural_buildings -i grammars/modern_district -o /tmp/seedb.obj -s 0,0,0,40,10,30 --seed 42 2>&1
diff /tmp/seeda.obj /tmp/seedb.obj && echo "IDENTICAL"
```

Expected: `IDENTICAL` — both runs produce the same output.

- [ ] **Step 3: Commit**

```bash
git add procedural_buildings/__main__.py
git commit -m "feat(cli): add --seed flag for reproducible builds"
```

---

### Task 1.3: `--validate` CLI flag

**Files:**
- Modify: `procedural_buildings/__main__.py`, `procedural_buildings/Processor.py`

- [ ] **Step 1: Add `validateGrammar` to `Processor.py`**

Before `grammarToManyObjs`, add:

```python
def validateGrammar(self, inFile, startRule="plot"):
    with open(inFile) as f:
        grammarText = f.read()
    self.grammarText = grammarText
    self.parse(grammarText)
    self.makeOps()
    self.process()
    self.simplify()
    return self
```

- [ ] **Step 2: Edit `__main__.py`**

Add `validate = False` to the local vars. Add `"validate"` to the long opts list (`--validate` is long-only). Add parsing:

```python
        elif opt == "--validate":
            validate = True
```

Before the `if not inFile or not outFile` check (around line 109), add:
```python
    if validate:
        if not inFile:
            log.error("Please provide an input file with -i for validation")
            print(usage)
            sys.exit(1)
        try:
            p = Processor()
            p.validateGrammar(inFile, startRule)
            log.info(f"Validation passed: {inFile}")
            sys.exit(0)
        except Exception as e:
            log.error(f"Validation failed: {e}")
            sys.exit(1)
```

Add `" [--validate]"` to the usage string.

Note: When `--validate` is set, no output file is needed. The error check at line 109 should be adjusted: skip the `outFile` requirement when `validate` is True.

```python
    if not validate and (not inFile or not outFile):
        log.error("Please provide both an input and output file")
```

- [ ] **Step 3: Verify**

```bash
cd /Users/vincent/Work/procedural-buildings
python -m procedural_buildings --validate -i grammars/orthodox_church 2>&1
echo "Exit code: $?"
```

Expected: "Validation passed" and exit code 0.

- [ ] **Step 4: Commit**

```bash
git add procedural_buildings/__main__.py procedural_buildings/Processor.py
git commit -m "feat(cli): add --validate flag for grammar linting"
```

---

### Task 1.4: Wire `grammars/op_tests/*` into pytest

**Files:**
- Create: `tests/test_op_grammars.py`

- [ ] **Step 1: Create `tests/test_op_grammars.py`**

```python
import os
import pytest
import numpy as np
from procedural_buildings.Processor import Processor
from procedural_buildings.Scope import Scope

OP_TESTS_DIR = "grammars/op_tests"
START_SCOPE = Scope.freshScope(np.array([0, 0, 0]), np.array([8, 8, 12]))


def _discover_op_tests():
    for name in sorted(os.listdir(OP_TESTS_DIR)):
        path = os.path.join(OP_TESTS_DIR, name)
        if os.path.isfile(path):
            yield path


@pytest.mark.parametrize("grammar_path", list(_discover_op_tests()))
def test_op_test_renders(grammar_path, tmp_path):
    p = Processor()
    out_path = str(tmp_path / "out.obj")
    p.grammarToManyObjs(grammar_path, "plot", START_SCOPE, 1, 0, out_path)
    assert os.path.exists(out_path), f"No OBJ written for {grammar_path}"
    assert os.path.getsize(out_path) > 0, f"Empty OBJ for {grammar_path}"
```

- [ ] **Step 2: Verify**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/test_op_grammars.py -v 2>&1 | tail -20
```

Expected: 10 tests all pass (conditions, constants, params, prim, priority, rand, randint, repeat, repeatN, split).

- [ ] **Step 3: Commit**

```bash
git add tests/test_op_grammars.py
git commit -m "test: wire grammars/op_tests into pytest as feature catalogue"
```

---

### Task 1.5: Round-trip test for BoxSplitter

**Files:**
- Create: `tests/test_round_trip.py`
- Modify: `procedural_buildings/Processor.py` (if needed for seed support in-process)

- [ ] **Step 1: Create `tests/test_round_trip.py`**

```python
import os
import random
import subprocess
import pytest
import numpy as np
from procedural_buildings.Processor import Processor
from procedural_buildings.Scope import Scope

SHOWCASE = [
    ("grammars/orthodox_church",     "plot", (0, 0, 0, 8, 8, 14)),
    ("grammars/soviet_block",        "plot", (0, 0, 0, 12, 8, 15)),
    ("grammars/material_building",   "plot", (0, 0, 0, 8, 8, 12)),
]

TOLERANCE = 4
SEED = 12345


def _parse_obj_vertices(path):
    verts = []
    with open(path) as f:
        for line in f:
            if line.startswith("v "):
                parts = line.split()
                if len(parts) >= 4:
                    x, y, z = parts[1], parts[2], parts[3]
                    verts.append((
                        round(float(x), TOLERANCE),
                        round(float(y), TOLERANCE),
                        round(float(z), TOLERANCE),
                    ))
    return frozenset(verts)


@pytest.mark.parametrize("grammar_path,start_rule,scope", SHOWCASE)
def test_round_trip_preserves_geometry(grammar_path, start_rule, scope, tmp_path):
    random.seed(SEED)
    np.random.seed(SEED)

    start_scope = Scope.freshScope(np.array(scope[:3]), np.array(scope[3:]))

    # Build 1
    p1 = Processor()
    out1 = str(tmp_path / "first.obj")
    p1.grammarToManyObjs(grammar_path, start_rule, start_scope, 1, 0, out1)
    v1 = _parse_obj_vertices(out1)
    assert len(v1) > 0, f"No vertices in {out1}"

    # Reverse
    out2 = str(tmp_path / "rebuilt_grammar")
    p2 = Processor()
    p2.objsToGrammar([out1], out2)

    # Rebuild
    p3 = Processor()
    out3 = str(tmp_path / "second.obj")
    p3.grammarToManyObjs(out2, start_rule, start_scope, 1, 0, out3)
    v2 = _parse_obj_vertices(out3)
    assert len(v2) > 0, f"No vertices in {out3}"

    missing = v1 - v2
    extra = v2 - v1
    assert not missing, f"{len(missing)} vertices lost in round-trip for {grammar_path}"
    assert not extra, f"{len(extra)} vertices added in round-trip for {grammar_path}"
```

- [ ] **Step 2: Verify**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/test_round_trip.py -v 2>&1 | tail -20
```

If tests fail, check the objsToGrammar API signature and adapt.

- [ ] **Step 3: Commit**

```bash
git add tests/test_round_trip.py
git commit -m "test: add BoxSplitter round-trip vertex equality test"
```

---

### Task 1.6: Golden snapshot tests

**Files:**
- Create: `tests/test_golden.py`, `tests/golden/hashes.json`
- Create: `scripts/update_golden.py`

- [ ] **Step 1: Create `tests/golden/hashes.json`**

```json
{}
```

- [ ] **Step 2: Create `tests/test_golden.py`**

```python
import hashlib
import json
import os
import random
import pytest
import numpy as np
from procedural_buildings.Processor import Processor
from procedural_buildings.Scope import Scope

GOLDEN_DIR = "tests/golden"
HASH_FILE = os.path.join(GOLDEN_DIR, "hashes.json")

REFERENCE = [
    ("orthodox_church",   "grammars/orthodox_church",    "plot", (0, 0, 0, 8, 8, 14), None),
    ("soviet",            "grammars/soviet_block",       "plot", (0, 0, 0, 12, 8, 15), None),
    ("material_solid",    "grammars/material_building",  "plot", (0, 0, 0, 8, 8, 12), None),
    ("material_checker",  "grammars/material_building",  "plot", (0, 0, 0, 8, 8, 12), "configs/checker.gin"),
]


def _canonicalise_obj(path):
    lines = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            lines.append(line)
    return "\n".join(sorted(lines)).encode("utf-8")


def _hash_file(path):
    return hashlib.sha256(_canonicalise_obj(path)).hexdigest()


def _load_hashes():
    if not os.path.exists(HASH_FILE):
        return {}
    with open(HASH_FILE) as f:
        return json.load(f)


@pytest.mark.parametrize("ref_id,grammar,rule,scope,_", REFERENCE)
def test_golden_hash(ref_id, grammar, rule, scope, tmp_path):
    random.seed(42)
    np.random.seed(42)

    start_scope = Scope.freshScope(np.array(scope[:3]), np.array(scope[3:]))

    gin_file = None
    for r in REFERENCE:
        if r[0] == ref_id and r[4] is not None:
            gin_file = r[4]
            break

    p = Processor()
    out = str(tmp_path / "out.obj")

    cwd = os.getcwd()
    try:
        if gin_file:
            os.chdir(os.path.dirname(os.path.abspath(gin_file)))
        p.grammarToManyObjs(grammar, rule, start_scope, 1, 0, out)
    finally:
        os.chdir(cwd)

    new_hash = _hash_file(out)
    stored = _load_hashes().get(ref_id)

    if stored is None:
        pytest.skip(f"No stored hash for {ref_id}; computed {new_hash[:12]}...")
    assert new_hash == stored, (
        f"Golden hash mismatch for {ref_id}:\n"
        f"  expected: {stored[:12]}\n"
        f"  got:      {new_hash[:12]}\n"
        f"If this change is intentional, run scripts/update_golden.py"
    )
```

- [ ] **Step 3: Create `scripts/update_golden.py`**

```python
#!/usr/bin/env python3
import json
import os
import random
import sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tests.test_golden import REFERENCE, _hash_file, GOLDEN_DIR
from procedural_buildings.Processor import Processor
from procedural_buildings.Scope import Scope

random.seed(42)
np.random.seed(42)

hashes = {}
for entry in REFERENCE:
    ref_id, grammar_file, rule, scope, gin_file = entry
    start_scope = Scope.freshScope(np.array(scope[:3]), np.array(scope[3:]))
    p = Processor()
    out = "/tmp/golden_out.obj"
    cwd = os.getcwd()
    try:
        if gin_file:
            os.chdir(os.path.dirname(os.path.abspath(gin_file)))
        p.grammarToManyObjs(grammar_file, rule, start_scope, 1, 0, out)
    finally:
        os.chdir(cwd)
    h = _hash_file(out)
    hashes[ref_id] = h
    print(f"{ref_id}: {h[:12]}...")

os.makedirs(GOLDEN_DIR, exist_ok=True)
with open(os.path.join(GOLDEN_DIR, "hashes.json"), "w") as f:
    json.dump(hashes, f, indent=2, sort_keys=True)
    f.write("\n")
print(f"Wrote {GOLDEN_DIR}/hashes.json")
```

- [ ] **Step 4: Run the update script to capture initial hashes**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config python scripts/update_golden.py 2>&1
```

Expected: 4 hashes written (orthodox_church, soviet, material_solid, material_checker).

- [ ] **Step 5: Run the golden tests**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/test_golden.py -v 2>&1 | tail -10
```

Expected: All 4 tests pass.

- [ ] **Step 6: Commit**

```bash
git add tests/test_golden.py tests/golden/hashes.json scripts/update_golden.py
git commit -m "test: add golden snapshot tests for 4 reference grammars"
```

---

### Task 1.7: Run all tests one final time

- [ ] **Step 1: Run the full test suite**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/ -v 2>&1 | tail -30
```

Expected: All existing 10 tests + ~50 grammar tests + 10 op_tests + 3 round-trip + 4 golden = ~77 tests pass.