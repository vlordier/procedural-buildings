# 2.5 — Colour Round-Trip Fix

## Goal
Fix the reverse-engineering path so that colour is preserved when a
building is written to OBJ and read back. Currently:
1. `ContextObj.addPrim` writes `o rect # colour(0.95,0.92,0.88)` —
   already correct.
2. `ObjReader.objToOpGraph` splits on `o `, uses `lines[0]` verbatim as
   `primName`, so prim names become `"rect # colour(0.95,0.92,0.88)"`.
3. The Box stores a broken primitive reference.
4. The reversed grammar never emits `OpColour` ops.
5. `scripts/obj_to_glb_colored.py` exists as a regex-based workaround.

After the fix: colour is parsed from the OBJ comment, attached to the
Box as a `colour` attribute, and the Box's OpPrimitive is wrapped in
`OpColour` at construction time.

## Approach: Leaf-level OpColour wrapping

Each `Box` stores an optional `colour` attribute. When present, the
Box wraps its `OpPrimitive` in `OpColour` inside `Box.__init__`. This
way the split tree (produced by `boxesToOp`) naturally inherits colour
at the leaf level without any post-processing pass.

### File: `scripts/obj_to_glb_colored.py` — DELETE

This file's sole purpose was to regex-recover colour from OBJ comment
lines. Now the engine is the source of truth. Delete the file.

### File: `tests/test_colour.py`

```python
import os
import pytest
import numpy as np
from procedural_buildings.ObjReader import objToOpGraph
from procedural_buildings.ContextObj import ContextObj
from procedural_buildings.Scope import Scope
from procedural_buildings.Ops import OpColour, OpPrimitive

def test_colour_written_to_obj_and_read_back(tmp_path):
    """Build a coloured scope, write OBJ, read it back, assert OpColour."""
    # Build
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([8, 8, 12]))
    ctx = ContextObj()
    ctx.colour((0.5, 0.3, 0.2), scope)
    op = OpPrimitive("rect")
    op.run(ctx, scope, {"width": 8, "depth": 8, "height": 12})
    obj_path = str(tmp_path / "test.obj")
    ctx.writeObj(obj_path)

    # Read back
    op_graph, _ = objToOpGraph(obj_path)
    assert op_graph is not None
    # Walk the op graph and look for OpColour
    found_colour = _find_op_colour(op_graph)
    assert found_colour, "No OpColour found in reversed graph"

def test_colour_values_preserved(tmp_path):
    """Assert RGB values are preserved through the round-trip."""
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([1, 1, 1]))
    ctx = ContextObj()
    ctx.colour((0.95, 0.92, 0.88), scope)
    OpPrimitive("rect").run(ctx, scope, {})
    ctx.writeObj(str(tmp_path / "test.obj"))

    op_graph, _ = objToOpGraph(str(tmp_path / "test.obj"))
    rgb = _extract_colour(op_graph)
    assert rgb is not None
    assert abs(rgb[0] - 0.95) < 0.01
    assert abs(rgb[1] - 0.92) < 0.01
    assert abs(rgb[2] - 0.88) < 0.01


def _find_op_colour(op):
    """Recursively search for an OpColour in the op tree."""
    if isinstance(op, OpColour):
        return True
    if hasattr(op, "childOps") and op.childOps:
        return any(_find_op_colour(c) for c in op.childOps)
    return False


def _extract_colour(op):
    """Recursively find and return the first OpColour's RGB."""
    if isinstance(op, OpColour):
        return op.args
    if hasattr(op, "childOps") and op.childOps:
        for c in op.childOps:
            result = _extract_colour(c)
            if result:
                return result
    return None
```

### Update: `tests/test_round_trip.py`

After the colour fix, update the round-trip test to include coloured
showcase grammars. The SHOWCASE list should add:

```python
("grammars/orthodox_church",   "plot", (0, 0, 0, 8, 8, 14)),
("grammars/soviet_block",      "plot", (0, 0, 0, 12, 8, 15)),
```

These previously failed because colour comments broke the reverse path.
Now they should pass.

## Testing
```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/test_colour.py tests/test_round_trip.py -v
```

Expected: colour tests pass, and showcase grammars now pass the
round-trip test.

## Out of scope
- Colour lifting (wrapping `OpColour` around `OpSplit` groups) — the
  leaf-level approach produces `colour(...){I(rect)}` per box rather
  than `colour(...){split(x){a|b|c}}`. This produces correct vertices
  but less clean grammar output. Cleaner output is a future improvement.
- `obj_to_glb.py` (the non-coloured version) — kept for tooling that
  doesn't need colour.
- Colour merging across adjacent identical boxes — each box currently
  gets its own `OpColour`. Merging is a simplification step that
  `Op.simplify` may or may not handle.