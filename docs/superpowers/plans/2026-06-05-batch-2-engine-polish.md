# Batch 2: Engine Polish & Content Implementation Plan

> **For agentic workers:** Use subagent-driven-development to implement.

**Goal:** 9 low-to-medium improvement items: magic string centralization, Lexer fix, 3 new ops/features, colour lifting, grammar fixes, new content, viewer improvements.

**Architecture:** Wave ordering: Wave 1 foundation (5 parallel), Wave 2 features (3 parallel after B1), Wave 3 content (after B7).

---

### Task B1: Centralize magic strings

**Files:**
- Create: `procedural_buildings/_names.py`
- Modify: `procedural_buildings/Lexer.py`, `Parser.py`, `Ops.py`, `Scope.py`

- [ ] **Step 1: Create `_names.py`**

```python
from enum import StrEnum


class OpName(StrEnum):
    SPLIT = "split"
    REPEAT = "repeat"
    REPEATN = "repeatN"
    COMP = "comp"
    COLOUR = "colour"
    NIL = "nil"
    I = "I"
    S = "S"
    T = "T"
    R = "R"
    SCALE = "scale"
    INSET = "inset"
    OPENING = "opening"
    DO = "do"
    FLIP = "flip"


class Axis(StrEnum):
    X = "x"
    Y = "y"
    Z = "z"


class Face(StrEnum):
    TOP = "top"
    BOTTOM = "bottom"
    FRONT = "front"
    BACK = "back"
    LEFT = "left"
    RIGHT = "right"
```

- [ ] **Step 2: Update `Ops.py` opName refs**

Replace each `opName = "split"` with `opName = OpName.SPLIT`, etc.

- [ ] **Step 3: Update `Lexer.py`**

Replace face name tokens with `Face` enum values.

- [ ] **Step 4: Update `Parser.py`**

Replace `axes = {"x": 0, ...}` with enum-based mapping.

- [ ] **Step 5: Update `Scope.py`**

Replace face-name if/elif with `Face` enum.

- [ ] **Step 6: Test and commit**

```bash
cd /Users/vincent/Work/procedural-buildings
ruff check --fix procedural_buildings/ && ruff format procedural_buildings/
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/ -q 2>&1 | tail -3
```

Commit: `git add -A && git commit -m "refactor: centralize op/axis/face names in _names.py StrEnum"`

---

### Task B2: Fix Lexer.error corruption

**Files:**
- Modify: `procedural_buildings/parsing/Lexer.py`, `procedural_buildings/parsing/GrammarParser.py`
- Test: `tests/test_parser.py`

- [ ] **Step 1: Modify `Lexer.py`**

Add `self.errors = []` in `__init__`. Change `error` to:
```python
def error(self, t):
    self.errors.append(f"Illegal character '{t.value[0]}' at line {self.lineno}")
    self.index += 1
```

- [ ] **Step 2: Modify `GrammarParser.py`**

After `lexer.tokenize(grammar)`, check `if lexer.errors: raise ...`.

- [ ] **Step 3: Add test**

```python
def test_lexer_bad_char_raises(self):
    lexer = Lexer()
    with pytest.raises(Exception, match="Illegal character"):
        list(lexer.tokenize("plot --> R(z, pi/6){I(rect)}"))
```

- [ ] **Step 4: Test and commit**

```bash
cd /Users/vincent/Work/procedural-buildings
ruff check --fix procedural_buildings/ tests/ && ruff format procedural_buildings/ tests/
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/ -q 2>&1 | tail -3
```

Commit: `git add -A && git commit -m "fix: Lexer.error collects errors and raises instead of silent corruption"`

---

### Task B3: flip(axis) op

**Files:**
- Modify: `procedural_buildings/Ops.py`, `procedural_buildings/parsing/Parser.py`, `procedural_buildings/parsing/Lexer.py`
- Create: `grammars/op_tests/flip`
- Test: `tests/test_ops.py`

- [ ] **Step 1: Add OpFlip to Ops.py**

```python
class OpFlip(Op):
    opName = OpName.FLIP

    def run(self, context, scope, env):
        axis = self.args.evaluate(env)[0]
        scope = scope.rotate(axis, math.pi)
        env = scope_env(env, scope)
        if self.childOps:
            self.childOps[0].run(context, scope, env)
```

- [ ] **Step 2: Add parser rule**

In Parser.py: `FLIP LPAR axis RPAR LCURL op RCURL`

- [ ] **Step 3: Add lexer token**

In Lexer.py: add `FLIP` to tokens.

- [ ] **Step 4: Add test**

```python
import math

def test_flip_runs():
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([8, 8, 12]))
    env = {"width": 8, "depth": 8, "height": 12}
    op = OpFlip(perChildArgs=("x",), childOps=[OpPrimitive("rect")])
    ctx = ContextObj()
    op.run(ctx, scope, env)
```

- [ ] **Step 5: Create op_test grammar**

`grammars/op_tests/flip`:
```
plot --> flip(x){I(rect)}
```

- [ ] **Step 6: Test and commit**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/ -q 2>&1 | tail -3
```

Commit: `git add -A && git commit -m "feat: add flip(axis) op as shorthand for R(axis, pi)"`

---

### Task B4: Multi-child rule bodies

**Files:**
- Modify: `procedural_buildings/parsing/Parser.py`
- Create: `grammars/op_tests/multi_body`

- [ ] **Step 1: Modify Parser.py**

When the grammar body contains `|`, the parser should split into multiple
(Left, Right) pairs instead of one. This allows:
```
rule --> I(rect) | I(triangle)
```
to be equivalent to:
```
rule --> I(rect) : 1
rule --> I(triangle) : 1
```

The exact production change depends on the Parser's grammar productions.
The approach: add a `PIPE` token to the lexer if not already present,
and add a production in `right_expr` that creates multiple Right objects.

- [ ] **Step 2: Create op_test grammar**

`grammars/op_tests/multi_body`:
```
plot --> I(rect) | I(triangle) | I(pyramid)
```

- [ ] **Step 3: Test and commit**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/ -q 2>&1 | tail -3
```

Commit: `git add -A && git commit -m "feat: multi-child rule bodies with | syntax"`

---

### Task B5: Env-conditional rules

**Files:**
- Modify: `procedural_buildings/Ops.py` (OpChooseRuleWithPriority.chooseChild)
- Create: `grammars/op_tests/env_conditions`

- [ ] **Step 1: Modify OpChooseRuleWithPriority**

In `chooseChild`, when evaluating conditions, include env variables
(width, depth, height, left_width, right_width, top_height, etc.)
in the evaluation symbol table so conditions like `width > 10` work.

- [ ] **Step 2: Create op_test grammar**

`grammars/op_tests/env_conditions`:
```
plot --> S(~1, ~1, 12){checkWidth}
checkWidth : width > 10 --> split(x){~1 : colour(1,0,0){I(rect)} | ~1 : colour(0,1,0){I(rect)}}
checkWidth : width <= 10 --> I(rect)
```

- [ ] **Step 3: Test and commit**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/ -q 2>&1 | tail -3
```

Commit: `git add -A && git commit -m "feat: env-conditional rules (width > 5 in conditions)"`

---

### Task B6: Colour lifting in reverse path

**Files:**
- Modify: `procedural_buildings/BoxSplitter.py`
- Test: `tests/test_colour.py`

- [ ] **Step 1: Add colour lifting function**

In `BoxSplitter.py`, add:
```python
def lift_colour(op):
    if not hasattr(op, "childOps") or not op.childOps:
        return op
    op.childOps = [lift_colour(c) for c in op.childOps]

    if isinstance(op, OpSplit):
        new_children = []
        i = 0
        while i < len(op.childOps):
            child = op.childOps[i]
            if isinstance(child, OpColour):
                group = [child.childOps[0]]
                j = i + 1
                while (j < len(op.childOps) and
                       isinstance(op.childOps[j], OpColour) and
                       op.childOps[j].args == child.args):
                    group.append(op.childOps[j].childOps[0])
                    j += 1
                if len(group) > 1:
                    sub_sizes = tuple(op.args.perChildArgs[k] for k in range(i, j))
                    sub_split = OpSplit(op.axis, perChildArgs=sub_sizes, childOps=group)
                    new_children.append(OpColour(child.args, childOps=[sub_split]))
                    i = j
                    continue
            new_children.append(child)
            i += 1
        op.childOps = new_children
    return op
```

Call `lift_colour` at the end of `boxesToOp()` before returning.

- [ ] **Step 2: Add test**

```python
def test_colour_lifting_merges_adjacent():
    # Build two adjacent same-colour boxes, reverse, assert single OpColour
    ...
```

- [ ] **Step 3: Test and commit**

```bash
cd /Users/vincent/Work/procedural-buildings
ruff check --fix procedural_buildings/ tests/ && ruff format procedural_buildings/ tests/
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/ -q 2>&1 | tail -3
```

Commit: `git add -A && git commit -m "feat: colour lifting merges adjacent same-colour boxes in reverse path"`

---

### Task B7: Fix 18 xfailed grammars

**Files:**
- Modify: `grammars/*` (various)
- Test: run full suite

- [ ] **Step 1: Run tests to list failures**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/test_grammars.py tests/test_op_grammars.py --tb=line -v 2>&1 | grep -E "XFAIL|FAIL"
```

- [ ] **Step 2: Fix each xfailed grammar**

For each grammar, either:
- **Fix**: add a `I(rect)` to produce geometry, add seed, or fix syntax
- **Archive**: move to `grammars/_archive/` if truly broken
- **Keep as xfail**: if it's a known edge case with no geometry output

Typical fixes:
- Add `I(rect)` to colour-only rules: `rule --> colour(0.5,0.5,0.5){I(rect)}`
- Add `random.seed(0)` or use `--seed` in tests

- [ ] **Step 3: Update xfail list and verify**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/ -q 2>&1 | tail -3
```

Expected: 0 xfailed.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "fix: resolve all 18 xfailed grammars"
```

---

### Task B8: Castle and bridge grammars

**Files:**
- Create: `grammars/castle`, `grammars/bridge`

- [ ] **Step 1: Create `grammars/castle`**

A medieval castle with keep, curtain walls, corner towers, crenellations.

- [ ] **Step 2: Create `grammars/bridge`**

A stone arch bridge with pillars and deck.

- [ ] **Step 3: Add to GRAMMAR_OVERRIDES if needed**

If the grammars use a non-default start rule or non-default scope.

- [ ] **Step 4: Test and commit**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/test_grammars.py -q 2>&1 | grep castle
```

Commit: `git add -A && git commit -m "feat: add castle and bridge showcase grammars"`

---

### Task B9: GLB viewer improvements

**Files:**
- Modify: `procedural_buildings/view.py`, `scripts/obj_to_glb.py`

- [ ] **Step 1: Improve viewer lighting and controls**

Add directional lighting, orbit controls, wireframe toggle to view.py.

- [ ] **Step 2: Improve GLB colour export**

Parse `# colour(r,g,b)` from OBJ and apply as material colour in GLB.

- [ ] **Step 3: Test**

```bash
cd /Users/vincent/Work/procedural-buildings
python -m procedural_buildings.view /tmp/example.obj
```

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: improve viewer lighting/orbit and GLB colour export"
```

---

### Task B10: Final verification

- [ ] **Step 1: Full test suite + lint**

```bash
cd /Users/vincent/Work/procedural-buildings
make test 2>&1 | tail -3
make lint 2>&1 | tail -3
```

- [ ] **Step 2: Commit any remaining changes**

```bash
git add -A
git commit -m "style: final formatting for batch 2"
```