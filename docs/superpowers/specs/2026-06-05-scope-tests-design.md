# 2.4 — Scope Method Tests

## Goal
Add unit tests for every public method on `Scope`:
`split`, `repeat`, `repeatN`, `comp`, `inset`, `opening`,
`translate`, `rotate`, `resize`, `scale`, `freshScope`.

## Approach
One test file `tests/test_scope.py`. Tests construct a known scope,
call the method, and assert the resulting scopes have correct
positions/sizes/rotations.

## File: `tests/test_scope.py`

```python
import pytest
import numpy as np
from procedural_buildings.Scope import Scope

ZERO = np.array([0.0, 0.0, 0.0])
POS = np.array([0.0, 0.0, 0.0])
SIZE = np.array([8.0, 8.0, 12.0])
```

### `Scope.split`

Create a scope of size (8, 8, 12). Split along z with relative sizes
(~4, ~4, ~4). Assert 3 child scopes with heights summing to 12.

```python
def test_split_creates_three_children():
    scope = Scope.freshScope(POS, SIZE)
    sizes = (Size(4, True), Size(4, True), Size(4, True))
    children = scope.split("z", sizes)
    assert len(children) == 3
    total_height = sum(c.size[2] for c in children)
    assert abs(total_height - 12.0) < 1e-6
```

### `Scope.repeat`

```python
def test_repeat_creates_children_of_repeat_size():
    scope = Scope.freshScope(POS, SIZE)
    children = scope.repeat("x", 2.0)
    assert len(children) == 4  # 8 / 2
    for c in children:
        assert abs(c.size[0] - 2.0) < 1e-6
```

### `Scope.repeatN`

```python
def test_repeat_n_creates_exact_count():
    scope = Scope.freshScope(POS, SIZE)
    children = scope.repeatN("z", 3)
    assert len(children) == 3
```

### `Scope.comp`

```python
def test_comp_creates_front_face():
    scope = Scope.freshScope(POS, np.array([8, 8, 12]))
    face = scope.comp("front")
    assert face is not None
    assert abs(face.size[0] - 8.0) < 1e-6  # width
    assert abs(face.size[2] - 12.0) < 1e-6  # height

def test_comp_creates_top_face():
    scope = Scope.freshScope(POS, np.array([8, 8, 12]))
    face = scope.comp("top")
    assert face is not None
    assert np.allclose(face.size, [8, 8, 0])  # depth = 0 for top

def test_comp_raises_for_invalid_face():
    scope = Scope.freshScope(POS, SIZE)
    with pytest.raises(ValueError):
        scope.comp("invalid_face")
```

### `Scope.inset`

```python
def test_inset_creates_inner_and_four_frame_boxes():
    scope = Scope.freshScope(POS, SIZE)
    inner_box, outer_boxes = scope.inset(1.0)
    assert inner_box is not None
    assert len(outer_boxes) == 4
    # Inner box should be 2 units smaller in each direction
    assert abs(inner_box.size[0] - 6.0) < 1e-6
    assert abs(inner_box.size[1] - 6.0) < 1e-6
```

### `Scope.opening`

```python
def test_opening_creates_inner_and_four_frame_scopes():
    scope = Scope.freshScope(POS, SIZE)
    child_scope, outer = scope.opening(1.0)
    assert child_scope is not None
    assert len(outer) == 4
    assert abs(child_scope.size[0] - 6.0) < 1e-6
    assert abs(child_scope.size[1] - 6.0) < 1e-6
```

### `Scope.translate`

```python
def test_translate_moves_scope():
    scope = Scope.freshScope(POS, SIZE)
    new_scope = scope.translate(np.array([1.0, 2.0, 3.0]))
    assert np.allclose(new_scope.pos, [1, 2, 3])
    assert np.allclose(new_scope.size, [8, 8, 12])
```

### `Scope.rotate`

```python
def test_rotate_around_z():
    scope = Scope.freshScope(POS, SIZE)
    rotated = scope.rotate("z", np.pi / 2)
    assert rotated is not None
    # Width/height still the same magnitude
    assert abs(rotated.size[0] - 8.0) < 1e-6
```

### `Scope.resize`

```python
def test_resize_changes_size():
    scope = Scope.freshScope(POS, SIZE)
    new_size = np.array([4.0, 8.0, 6.0])
    resized = scope.resize(new_size)
    assert np.allclose(resized.size, [4, 8, 6])
```

### `Scope.scale`

```python
def test_scale_multiplies_size():
    scope = Scope.freshScope(POS, SIZE)
    scaled = scope.scale(0.5)
    assert np.allclose(scaled.size, [4, 4, 6])
```

### `Scope.freshScope`

```python
def test_fresh_scope_creates_correct_size():
    scope = Scope.freshScope(ZERO, np.array([1.0, 2.0, 3.0]))
    assert np.allclose(scope.pos, [0, 0, 0])
    assert np.allclose(scope.size, [1, 2, 3])
```

## Testing
```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/test_scope.py -v
```

Expected: 12+ tests, all pass.

## Out of scope
- Testing neighbor propagation during split (covered by test_env.py)
- Testing `calcScale` or `putVertsInScope` (internal helpers, tested
  indirectly by the split/comp/inset tests)