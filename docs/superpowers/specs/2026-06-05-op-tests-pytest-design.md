# 1.4 — Wire `grammars/op_tests/*` into Pytest

## Goal
The 10 grammar files in `grammars/op_tests/` (`conditions`, `constants`,
`params`, `prim`, `priority`, `rand`, `randint`, `repeat`, `repeatN`,
`split`) are the engine's feature catalogue. They should run as tests, not
sit in the showcase directory as documentation.

## Approach
Two parts:
1. Move the directory to `tests/grammars/op_tests/` (or keep the location
   but exclude from `test_grammars.py`).
2. Add `tests/test_op_grammars.py` that parametrises over each op_tests
   file and asserts it renders.

## Decision: keep location, exclude from item 1.1

Moving the directory would invalidate a lot of relative paths and
documentation. Instead:
- `test_grammars.py` skips `op_tests/`.
- A new `tests/test_op_grammars.py` discovers and tests them.

This is also more honest: op_tests is a test artefact, but moving it
inside `tests/` may break the grammar's ability to reference sibling
primitives (if it ever does — current op_tests don't).

## File: `tests/test_op_grammars.py`

```python
import os
import pytest
import numpy as np
from procedural_buildings.Processor import Processor
from procedural_buildings.Scope import Scope

OP_TESTS_DIR = "grammars/op_tests"
START_SCOPE = Scope.freshScope(
    np.array([0, 0, 0]), np.array([8, 8, 12])
)


def _discover_op_tests():
    for name in sorted(os.listdir(OP_TESTS_DIR)):
        path = os.path.join(OP_TESTS_DIR, name)
        if os.path.isfile(path):
            yield path, "plot"


@pytest.mark.parametrize("grammar_path,start_rule",
                         list(_discover_op_tests()))
def test_op_test_renders(grammar_path, start_rule, tmp_path):
    p = Processor()
    out_path = str(tmp_path / "out.obj")
    p.grammarToManyObjs(
        grammar_path, start_rule, START_SCOPE, 1, 0, out_path
    )
    assert os.path.exists(out_path)
    assert os.path.getsize(out_path) > 0
```

## Update to `test_grammars.py`
Add `op_tests` to `SKIP_DIRS`:
```python
SKIP_DIRS = {"_archive", "op_tests", "__pycache__"}
```

## Catalogue doc
Add a one-line comment at the top of `test_op_grammars.py` listing what
each op_test exercises:

```python
# op_tests feature catalogue:
#   conditions  -- conditional rule dispatch
#   constants   -- grammar-level constants
#   params      -- parameterised rules
#   prim        -- primitive references
#   priority    -- OpChooseRuleWithPriority
#   rand        -- rand() in expressions
#   randint     -- randint() in expressions
#   repeat      -- repeat() op
#   repeatN     -- repeatN() op
#   split       -- split() op
```

## Acceptance
- `pytest tests/test_op_grammars.py -v` runs 10 tests, all pass.
- `pytest tests/test_grammars.py -v` no longer touches `op_tests/`.
- Each op_test is a runnable, documented example of a single engine feature.

## Out of scope
- Asserting that op_tests produce *meaningful* output (e.g., a `repeat`
  test should produce multiple boxes). The current smoke test only checks
  "no exception + non-empty output". Tightening this is a future item.
