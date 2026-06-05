# 1.5 — `BoxSplitter` Round-Trip Test

## Goal
Verify that the engine's signature feature — reverse engineering a built
model into a grammar — produces the same geometry on re-build. For each
showcase grammar, build → reverse → re-build → assert vertex set equality
(permuted).

## Approach
For each of 5 showcase grammars (orthodox_church, european_townhouse,
warehouse_district, soviet_block, material_building):
1. Render to OBJ.
2. Run `Processor.objsToGrammar` (or its reverse pipeline) to get an op graph.
3. Re-render the op graph to OBJ.
4. Parse both OBJs to vertex sets.
5. Assert the sets are equal (modulo ordering).

**Definition of equality (locked):** vertex sets as `frozenset` of
`(x, y, z)` tuples, with coordinates rounded to 4 decimal places. Floating
point arithmetic in the reverse path can produce 1e-15 drift; 4 decimals
is well below visible threshold and above noise.

## File: `tests/test_round_trip.py`

```python
import os
import re
import subprocess
import pytest
import numpy as np
from procedural_buildings.Processor import Processor
from procedural_buildings.Scope import Scope

SHOWCASE = [
    ("grammars/orthodox_church",     "plot", (0, 0, 0, 8, 8, 14)),
    ("grammars/european_townhouse",  "plot", (0, 0, 0, 8, 8, 12)),
    ("grammars/warehouse_district",  "block",(0, 0, 0, 40, 10, 20)),
    ("grammars/soviet_block",        "plot", (0, 0, 0, 12, 8, 15)),
    ("grammars/material_building",   "plot", (0, 0, 0, 8, 8, 12)),
]

TOLERANCE = 4  # decimal places


def _parse_obj_vertices(path):
    """Return frozenset of (x, y, z) tuples rounded to TOLERANCE decimals."""
    verts = []
    with open(path) as f:
        for line in f:
            if line.startswith("v "):
                _, x, y, z = line.split()[:4]
                verts.append((
                    round(float(x), TOLERANCE),
                    round(float(y), TOLERANCE),
                    round(float(z), TOLERANCE),
                ))
    return frozenset(verts)


@pytest.mark.parametrize("grammar_path,start_rule,scope",
                         [(g, r, s) for g, r, s in SHOWCASE])
def test_round_trip_preserves_geometry(grammar_path, start_rule, scope,
                                        tmp_path, monkeypatch):
    # Build 1
    p1 = Processor()
    out1 = str(tmp_path / "first.obj")
    startScope = Scope.freshScope(
        np.array(scope[:3]), np.array(scope[3:])
    )
    p1.grammarToManyObjs(grammar_path, start_rule, startScope, 1, 0, out1)
    v1 = _parse_obj_vertices(out1)

    # Reverse
    p2 = Processor()
    out2 = str(tmp_path / "rebuilt.obj")
    p2.objsToGrammar([out1], out2)
    p2.grammarToManyObjs(out2, start_rule, startScope, 1, 0, str(tmp_path / "second.obj"))

    v2 = _parse_obj_vertices(str(tmp_path / "second.obj"))

    # Compare
    missing = v1 - v2
    extra = v2 - v1
    assert not missing, f"Vertices lost in round-trip: {len(missing)} missing"
    assert not extra, f"Vertices added in round-trip: {len(extra)} extra"
```

## Reverse pipeline investigation

`Processor.objsToGrammar` takes a list of OBJ files and writes a grammar.
The internal call chain is approximately: ObjReader → BoxSplitter → op
graph → simplify → toGrammarText. The plan executor should confirm the
exact API and adapt the test code to match.

**If `objsToGrammar` cannot be called twice in one process** (because
singleton state in Processor), use a subprocess invocation:

```python
# In the test:
subprocess.run(
    ["python", "-m", "procedural_buildings",
     "-i", out1, "-o", out2, "-r", "--start_rule", start_rule],
    check=True,
)
```

## Known limitation: colour round-trip
The current `ObjReader` does not parse colour comments in the OBJ (see
cluster 2). The round-trip test should NOT assert colour equality — only
vertex equality. Once cluster 2 lands the engine-native colour recovery,
this test can be tightened to assert colour-tagged vertex sets.

## Acceptance
- `pytest tests/test_round_trip.py -v` runs 5 tests.
- All 5 pass: each showcase grammar survives build→reverse→rebuild.
- A deliberate change to a grammar (e.g., add a window) causes at least
  one test to fail with a clear diff.

## Out of scope
- Round-trip on `random`-using grammars (e.g., `european_townhouse` uses
  `rand/2 + 0.5`). The test will be non-deterministic for those; the plan
  will document this and either seed them or mark xfail.
- Property tests over the BoxSplitter algorithm itself (covered in
  cluster 2 by `test_ops.py` and `test_simplify.py`).
