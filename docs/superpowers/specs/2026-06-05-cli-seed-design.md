# 1.2 — `--seed` Flag for Reproducible Builds

## Goal
Add a `--seed N` flag to the CLI that, when set, makes the run deterministic.
Same seed + same inputs → byte-identical output.

## Approach
Seed `random` and `numpy.random` once, before `Processor.grammarToManyObjs`
is called. The existing engine uses `rand`, `randint`, and `randrange` from
Python's `random` module via grammar expressions, and `numpy.random` in some
geometry paths.

## File: `procedural_buildings/__main__.py`

Add `seed = None` to the local vars. Add `"seed="` to the long opts. Parse
the option. Seed both RNGs at the top of `main()` (or just before Processor
is constructed).

```python
import random
import numpy as np

# In main():
seed = None
# In opts loop:
elif opt in ("--seed",):
    try:
        seed = int(arg)
    except ValueError:
        log.error("Error: --seed must be an integer")
        sys.exit(2)

# After option parsing, before Processor():
if seed is not None:
    random.seed(seed)
    np.random.seed(seed)
```

Add to the long opts:
```python
"seed=",
```

Add to the short opts (none — this is a long-only flag to keep `getopt` simple).

Add to the usage string:
```
" [--seed <N>]"
```

## Test
```python
# tests/test_cli_seed.py
import subprocess
import os

def test_seed_produces_deterministic_output(tmp_path):
    out1 = tmp_path / "out1.obj"
    out2 = tmp_path / "out2.obj"
    cmd = [
        "python", "-m", "procedural_buildings",
        "-i", "grammars/modern_district",
        "-o", str(out1),
        "-s", "0,0,0,40,10,30",
        "--seed", "42",
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    cmd2 = list(cmd)
    cmd2[cmd2.index(str(out1))] = str(out2)
    subprocess.run(cmd2, check=True, capture_output=True)
    assert out1.read_bytes() == out2.read_bytes()

def test_no_seed_does_not_raise():
    subprocess.run(
        ["python", "-m", "procedural_buildings",
         "-i", "grammars/modern_district",
         "-o", "/tmp/seedless.obj",
         "-s", "0,0,0,40,10,30"],
        check=True, capture_output=True,
    )
```

## Acceptance
- `python -m procedural_buildings -i grammars/modern_district -o /tmp/a.obj -s 0,0,0,40,10,30 --seed 42`
- Then the same with `--seed 42` again produces a byte-identical `/tmp/b.obj`.
- A run without `--seed` is unchanged from current behaviour.

## Out of scope
- Per-grammar seeding (one global seed is enough).
- Reproducibility for the reverse path (`-r`) — that's a future item once
  the colour round-trip is fixed in cluster 2.
