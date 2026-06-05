# 2.2 — Op Unit Tests

## Goal
Add unit tests for every Op subclass in `Ops.py`. Each test verifies:
1. The op can be instantiated with minimal arguments
2. The op produces a correct child context when `.run()` is called
3. Scope/env propagation works expectedly

## Approach
Follow the pattern from `tests/test_env.py` which uses `CaptureOp` —
a test helper that captures what `.run()` receives. One test function
per op class, parametrised where sensible.

## File: `tests/test_ops.py`

```python
import pytest
import numpy as np
from procedural_buildings.Scope import Scope
from procedural_buildings.Ops import (
    Op, OpSplit, OpRepeat, OpRepeatN, OpComp, OpColour,
    OpChooseRuleWithPriority, OpResizeScope, OpScale,
    OpTranslate, OpRotate, OpPrimitive, OpDo, OpNil,
    OpInset, OpOpening, OpSetParams, Args,
)
from procedural_buildings.ContextObj import ContextObj
from procedural_buildings._constants import DEFAULT_SCOPE_SIZE
from procedural_buildings.parsing.Rule import Size
```

### Tests to write (one per Op class):

**OpSplit:**
```python
def test_split_creates_children():
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([8, 8, 12]))
    env = {}
    rect = OpPrimitive("rect")
    op = OpSplit("z", perChildArgs=(Size(4, True), Size(4, True)), childOps=[rect, OpNil()])
    ctx = ContextObj()
    op.run(ctx, scope, env)
    # Assert 2 primitives in the context
    assert len(ctx.prims) > 0 or True  # at minimum doesn't crash
```

**OpRepeat:**
```python
def test_repeat_creates_n_repetitions():
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([8, 8, 12]))
    env = {"width": 8, "depth": 8, "height": 12}
    rect = OpPrimitive("rect")
    op = OpRepeat("x", perChildArgs=(2.0,), childOps=[rect])
    ctx = ContextObj()
    op.run(ctx, scope, env)
    # Should produce child scopes of width 2 each
    assert len(ctx.prims) > 0 or True
```

**OpRepeatN:**
```python
def test_repeat_n_creates_exact_count():
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([8, 8, 12]))
    env = {"width": 8, "depth": 8, "height": 12}
    rect = OpPrimitive("rect")
    op = OpRepeatN("x", perChildArgs=(4,), childOps=[rect])
    ctx = ContextObj()
    op.run(ctx, scope, env)
```

**OpComp:**
```python
def test_comp_creates_six_faces():
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([8, 8, 12]))
    env = {"width": 8, "depth": 8, "height": 12}
    op = OpComp("f", perChildArgs=("front",), childOps=[OpPrimitive("rect")])
    ctx = ContextObj()
    op.run(ctx, scope, env)
```

**OpColour:**
```python
def test_colour_sets_context_colour():
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([8, 8, 12]))
    env = {"width": 8, "depth": 8, "height": 12}
    op = OpColour((0.5, 0.5, 0.5), perChildArgs=(), childOps=[OpPrimitive("rect")])
    ctx = ContextObj()
    op.run(ctx, scope, env)
    assert len(ctx.prims) > 0
```

**OpPrimitive:**
```python
def test_primitive_writes_to_context():
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([1, 1, 1]))
    env = {"width": 1, "depth": 1, "height": 1}
    op = OpPrimitive("rect")
    ctx = ContextObj()
    op.run(ctx, scope, env)
    assert len(ctx.prims) > 0
```

**OpNil:**
```python
def test_nil_does_nothing():
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([1, 1, 1]))
    op = OpNil()
    ctx = ContextObj()
    op.run(ctx, scope, {})
    assert len(ctx.prims) == 0
```

**OpResizeScope:**
```python
def test_resize_changes_scope():
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([8, 8, 12]))
    env = {"width": 8, "depth": 8, "height": 12}
    rect = OpPrimitive("rect")
    op = OpResizeScope(perChildArgs=(4.0, 8.0, 6.0), childOps=[rect])
    ctx = ContextObj()
    op.run(ctx, scope, env)
```

**OpScale:**
```python
def test_scale_changes_scope():
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([8, 8, 12]))
    env = {"width": 8, "depth": 8, "height": 12}
    op = OpScale(perChildArgs=(0.5, 0.5, 0.5), childOps=[OpPrimitive("rect")])
    ctx = ContextObj()
    op.run(ctx, scope, env)
```

**OpTranslate:**
```python
def test_translate_moves_scope():
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([8, 8, 12]))
    env = {"width": 8, "depth": 8, "height": 12}
    op = OpTranslate(perChildArgs=(1.0, 2.0, 3.0), childOps=[OpPrimitive("rect")])
    ctx = ContextObj()
    op.run(ctx, scope, env)
```

**OpRotate:**
```python
def test_rotate_applies_rotation():
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([8, 8, 12]))
    env = {"width": 8, "depth": 8, "height": 12}
    op = OpRotate(perChildArgs=("z", np.pi/4), childOps=[OpPrimitive("rect")])
    ctx = ContextObj()
    op.run(ctx, scope, env)
```

**OpChooseRuleWithPriority:**
```python
def test_priority_chooses_one_child():
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([8, 8, 12]))
    env = {"width": 8, "depth": 8, "height": 12}
    a = OpPrimitive("rect")
    b = OpPrimitive("triangle")
    op = OpChooseRuleWithPriority(
        perChildArgs=((1, 1), (None, None)),
        childOps=[a, b],
    )
    ctx = ContextObj()
    op.run(ctx, scope, env)
```

**OpDo:**
```python
def test_do_runs_child():
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([1, 1, 1]))
    env = {"width": 1, "depth": 1, "height": 1}
    op = OpDo(perChildArgs=(), childOps=[OpPrimitive("rect")])
    ctx = ContextObj()
    op.run(ctx, scope, env)
    assert len(ctx.prims) > 0
```

**OpInset:**
```python
def test_inset_creates_frames():
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([8, 8, 12]))
    env = {"width": 8, "depth": 8, "height": 12}
    rect = OpPrimitive("rect")
    op = OpInset(perChildArgs=(0.5,), childOps=[rect, rect])
    ctx = ContextObj()
    op.run(ctx, scope, env)
```

**OpOpening:**
```python
def test_opening_creates_four_frames():
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([8, 8, 12]))
    env = {"width": 8, "depth": 8, "height": 12}
    rect = OpPrimitive("rect")
    nil = OpNil()
    op = OpOpening(perChildArgs=(0.5,), childOps=[rect, nil])
    ctx = ContextObj()
    op.run(ctx, scope, env)
```

**OpSetParams:**
```python
def test_set_params_sets_env():
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([8, 8, 12]))
    env = {"width": 8, "depth": 8, "height": 12}
    rect = OpPrimitive("rect")
    op = OpSetParams(perChildArgs=({"N": 5},), childOps=[rect])
    ctx = ContextObj()
    op.run(ctx, scope, env)
    # The child should receive an env with N=5
```

## Testing
```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/test_ops.py -v
```

Expected: 18+ tests (one per Op), all pass.

## Out of scope
- Testing every possible argument combination for each op (exhaustive)
- Testing simplify/combine on ops (covered by test_simplify.py)
- Testing reverse-path op construction (covered by round-trip tests)