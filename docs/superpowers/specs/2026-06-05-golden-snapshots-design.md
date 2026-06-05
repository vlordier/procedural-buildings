# 1.6 — Golden Snapshot Tests

## Goal
Detect unintentional geometry drift in showcase grammars. Five reference
grammars render to a stable hash of the OBJ contents; the hash is checked
into the repo. If a change to the engine or grammar causes the output to
differ, the test fails with a clear diff message.

## Approach
1. Generate the canonical OBJ for each reference grammar (with `--seed 42`
   to make it deterministic).
2. Hash the file contents (sha256, excluding comment lines and whitespace
   variations).
3. Store the hash in `tests/golden/hashes.json`.
4. The test re-renders with the same seed, hashes, and compares.

## Why hash and not literal OBJ?
OBJ file content includes comments (timestamps, etc.) and may have
ordering variations across runs. Hashing the canonicalised content (sorted
non-blank, non-comment lines) gives a stable signal that catches real
geometry drift while tolerating benign reordering.

## File: `tests/test_golden.py`

```python
import hashlib
import json
import os
import pytest
import numpy as np
from procedural_buildings.Processor import Processor
from procedural_buildings.Scope import Scope

GOLDEN_DIR = "tests/golden"
HASH_FILE = os.path.join(GOLDEN_DIR, "hashes.json")

REFERENCE = [
    ("orthodox_church",   "grammars/orthodox_church",    "plot", (0, 0, 0, 8, 8, 14)),
    ("townhouse",         "grammars/european_townhouse", "plot", (0, 0, 0, 8, 8, 12)),
    ("soviet",            "grammars/soviet_block",       "plot", (0, 0, 0, 12, 8, 15)),
    ("material_solid",    "grammars/material_building",  "plot", (0, 0, 0, 8, 8, 12)),
    ("material_checker",  "grammars/material_building",  "plot", (0, 0, 0, 8, 8, 12),
        "configs/checker.gin"),
]


def _canonicalise_obj(path):
    """Return sorted, stripped, comment-free lines."""
    with open(path) as f:
        lines = []
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


@pytest.mark.parametrize("ref_id,grammar,rule,scope",
                         [(r[0], r[1], r[2], r[3]) for r in REFERENCE])
def test_golden_hash(ref_id, grammar, rule, scope, tmp_path):
    gin_file = None
    for r in REFERENCE:
        if r[0] == ref_id and len(r) == 5:
            gin_file = r[4]
            break

    p = Processor()
    out = str(tmp_path / "out.obj")
    startScope = Scope.freshScope(
        np.array(scope[:3]), np.array(scope[3:])
    )

    # If a gin file is associated, copy it into the grammar dir for the
    # Processor to find (Processor's grammarDir is cwd by default).
    cwd_save = os.getcwd()
    try:
        if gin_file:
            os.chdir(os.path.dirname(os.path.abspath(gin_file)))
        p.grammarToManyObjs(grammar, rule, startScope, 1, 0, out)
    finally:
        os.chdir(cwd_save)

    new_hash = _hash_file(out)
    stored = _load_hashes().get(ref_id)

    if stored is None:
        # First run: store the hash, mark test as "to be reviewed".
        pytest.skip(f"No stored hash for {ref_id}; computed {new_hash[:12]}...")
    assert new_hash == stored, (
        f"Golden hash mismatch for {ref_id}:\n"
        f"  expected: {stored[:12]}\n"
        f"  got:      {new_hash[:12]}\n"
        f"If this change is intentional, run scripts/update_golden.py"
    )
```

## Initial hash capture
A small script `scripts/update_golden.py` runs each reference grammar with
seed 42 and writes `hashes.json`. This is run once during cluster 1
implementation, and re-run only when a change is intentional.

```python
# scripts/update_golden.py
import json
import os
import sys
sys.path.insert(0, ".")
from tests.test_golden import REFERENCE, _hash_file, _canonicalise_obj, GOLDEN_DIR
from procedural_buildings.Processor import Processor
from procedural_buildings.Scope import Scope
import numpy as np

hashes = {}
for entry in REFERENCE:
    ref_id, grammar, rule, scope = entry[:4]
    gin_file = entry[4] if len(entry) == 5 else None
    p = Processor()
    out = "/tmp/golden.obj"
    startScope = Scope.freshScope(
        np.array(scope[:3]), np.array(scope[3:])
    )
    cwd = os.getcwd()
    try:
        if gin_file:
            os.chdir(os.path.dirname(os.path.abspath(gin_file)))
        p.grammarToManyObjs(grammar, rule, startScope, 1, 0, out)
    finally:
        os.chdir(cwd)
    hashes[ref_id] = _hash_file(out)
    print(f"{ref_id}: {hashes[ref_id][:12]}")

os.makedirs(GOLDEN_DIR, exist_ok=True)
with open(os.path.join(GOLDEN_DIR, "hashes.json"), "w") as f:
    json.dump(hashes, f, indent=2, sort_keys=True)
```

## Acceptance
- `pytest tests/test_golden.py -v` runs 5 tests; first run skips with a
  "no stored hash" message. After running `scripts/update_golden.py` and
  committing `tests/golden/hashes.json`, all 5 pass.
- An unintentional change to a showcase grammar (e.g., typo) causes a
  test to fail with the expected/got hash diff.
- An intentional change can be accepted by re-running the update script
  and committing the new hash.

## Out of scope
- Hashing the *reverse* path output (that's item 1.5).
- Hashing intermediate op graphs.
- Per-OS or per-Python-version hashes (the seed-based determinism should
  make this stable; if it isn't, that's a separate bug to fix).
