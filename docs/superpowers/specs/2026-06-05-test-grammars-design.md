# 1.1 — Auto-discover and Render Every Grammar

## Goal
A single pytest file that, on every run, parses and renders every grammar in
`grammars/` (excluding `_archive/`). Catches the next grammar bug for free.

## Approach
`tests/test_grammars.py` walks the `grammars/` directory, skips `_archive/`
and `op_tests/` (covered by item 1.4), and for each `.grammar` file (or file
without an extension — current convention) does:
1. Read the file.
2. Run `Processor.grammarToManyObjs` with `-s 0,0,0,8,8,12` and a tmp
   output path. Catch any exception.
3. Assert the output OBJ exists and is non-empty.

## File: `tests/test_grammars.py`

```python
import os
import tempfile
import pytest
import numpy as np
from procedural_buildings.Processor import Processor
from procedural_buildings.Scope import Scope

GRAMMARS_DIR = "grammars"
SKIP_DIRS = {"_archive", "op_tests", "__pycache__"}
START_SCOPE = Scope.freshScope(
    np.array([0, 0, 0]), np.array([8, 8, 12])
)


def _discover_grammars():
    """Yield (path, start_rule) for every grammar in grammars/."""
    for entry in sorted(os.listdir(GRAMMARS_DIR)):
        path = os.path.join(GRAMMARS_DIR, entry)
        if not os.path.isfile(path):
            continue
        if entry.startswith("."):
            continue
        # Each grammar file uses its own start rule; the file's base name
        # is the rule if the grammar doesn't override. Default to "plot".
        yield path, "plot"


@pytest.mark.parametrize("grammar_path,start_rule", list(_discover_grammars()))
def test_grammar_renders(grammar_path, start_rule, tmp_path):
    p = Processor()
    out_path = str(tmp_path / "out.obj")
    p.grammarToManyObjs(
        grammar_path, start_rule, START_SCOPE, 1, 0, out_path
    )
    assert os.path.exists(out_path), f"No OBJ written for {grammar_path}"
    assert os.path.getsize(out_path) > 0, f"Empty OBJ for {grammar_path}"
```

## Per-grammar overrides
Some grammars need a non-default start rule or a larger scope. We'll handle
these two ways:
1. **By convention** — the test harness tries `plot` first; if that fails
   with a "no rule named plot" error, it falls back to the file's base name.
2. **By override map** — a small dict at the top of the test file lists
   `{"grammars/site_layout": ("block", (0, 0, 0, 40, 10, 20)), ...}` for
   grammars that need explicit start rule and scope.

```python
GRAMMAR_OVERRIDES = {
    "grammars/site_layout":       ("block", (0, 0, 0, 40, 10, 20)),
    "grammars/warehouse_district":("block", (0, 0, 0, 40, 10, 20)),
    "grammars/modern_district":   ("district", (0, 0, 0, 40, 10, 30)),
    "grammars/neighbor_facade":   ("plot", (0, 0, 0, 8, 8, 12)),
}
```

## Discovery exclusions
- Files inside `_archive/` (no rendering).
- Files inside `op_tests/` (covered by item 1.4).
- Hidden files (`.DS_Store`, etc.).
- The README, if one is added (handled by isfile check + extension).

## Skipping vs failing
Some grammars may legitimately fail for reasons unrelated to bugs (missing
primitive `.obj` files, etc.). The test should be parametrized with an
`xfail` marker for known-broken grammars:

```python
XFAIL_GRAMMARS = {
    "grammars/foo",      # scratch file
    "grammars/window",   # references missing primitive
    "grammars/cabin",    # references missing primitive
    "grammars/overlap",  # exploits undocumented behaviour
}
```

These will be deleted in cluster 3 anyway. Once cluster 3 lands, the xfail
list shrinks to empty.

## Testing
```bash
pytest tests/test_grammars.py -v
```
Expected: ~50 tests (one per showcase grammar), all pass. The 4 xfail
grammars are expected failures.

## Out of scope
- This test does NOT verify geometry, only that the grammar runs.
- Geometry verification is items 1.5 (round-trip) and 1.6 (golden).
