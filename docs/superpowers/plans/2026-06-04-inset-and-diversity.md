# Inset Operation & Primitive Diversity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an `inset` CGA operation for creating recessed panels/frames and add 5 new architectural primitives (arch, column, balcony, dormer, pediment).

**Architecture:** One new op class (`OpInset`), one new scope method (`Scope.inset`), lexer/parser extension for the `inset` keyword, and 5 OBJ primitive files. No new dependencies.

**Tech Stack:** Python 3.12, numpy, sly

---

### Task 1: Scope.inset() method

**Files:**
- Modify: `procedural_buildings/Scope.py` (add inset method after `repeatN`)

- [ ] **Step 1: Add `inset` method to Scope**

Add after `repeatN` (line 99):

```python
def inset(self, amount):
    s = self.size
    d = amount
    top = Scope(self.pos + self.rotMat.dot(np.array([0, 0, s[2] - d])), self.rotMat, np.array([s[0], d, 0]))
    bottom = Scope(self.pos, self.rotMat, np.array([s[0], d, 0]))
    left = Scope(self.pos + self.rotMat.dot(np.array([0, d, 0])), self.rotMat, np.array([d, s[1] - 2 * d, 0]))
    right = Scope(self.pos + self.rotMat.dot(np.array([s[0] - d, d, 0])), self.rotMat, np.array([d, s[1] - 2 * d, 0]))
    inner = Scope(self.pos + self.rotMat.dot(np.array([d, d, 0])), self.rotMat, np.array([s[0] - 2 * d, s[1] - 2 * d, 0]))
    return [top, bottom, left, right], inner
```

Note: `inset` works in the XY plane (z-up convention). The frame scopes have zero depth (z=0) since they're 2D faces of the inset boundary. The inner scope has the same depth as the original scope.

- [ ] **Step 2: Compile check**

Run: `python3 -m py_compile procedural_buildings/Scope.py`
Expected: no errors

- [ ] **Step 3: Commit**

```bash
git add procedural_buildings/Scope.py
git commit -m "feat: add Scope.inset() for generating inset/frame scopes"
```

---

### Task 2: OpInset class

**Files:**
- Modify: `procedural_buildings/Ops.py` (add OpInset class after OpNil)

- [ ] **Step 1: Add OpInset class**

Add after `OpNil`:

```python
# Create an inset (recessed panel with frame) in the current scope
class OpInset(Op):

    opName = "inset"

    def run(self, context, scope, env):
        (amount,) = self.args.evaluate(env)
        frameOp = self.childOps[0]
        innerOp = self.childOps[1]
        frameScopes, innerScope = scope.inset(amount)
        for frameScope in frameScopes:
            frameOp.run(context, frameScope, env)
        innerOp.run(context, innerScope, env)

    def simplify(self, seenOps, combArgs=False):
        childOps = [c.simplify(seenOps, combArgs) for c in self.childOps]
        ident = ("OpInset", self.args[0])
        myHash = hash(ident)
        if myHash in seenOps:
            return seenOps[myHash]
        newOp = OpInset(self.args[0], childOps=childOps)
        seenOps[myHash] = newOp
        newOp.hash = myHash
        return newOp

    def argsToHash(self):
        return [self.__class__.__name__, self.args[0]]
```

- [ ] **Step 2: Compile check**

Run: `python3 -m py_compile procedural_buildings/Ops.py`
Expected: no errors

- [ ] **Step 3: Commit**

```bash
git add procedural_buildings/Ops.py
git commit -m "feat: add OpInset operation for recessed panels and frames"
```

---

### Task 3: Lexer INSET token

**Files:**
- Modify: `procedural_buildings/parsing/Lexer.py`

- [ ] **Step 1: Add INSET to token set**

Add `INSET,` after `SCALE` in the tokens set.

- [ ] **Step 2: Add INSET keyword mapping**

Add after `IDENT["scale"] = SCALE`:
```python
IDENT["inset"] = INSET
```

- [ ] **Step 3: Compile check**

Run: `python3 -m py_compile procedural_buildings/parsing/Lexer.py`
Expected: no errors

- [ ] **Step 4: Commit**

```bash
git add procedural_buildings/parsing/Lexer.py
git commit -m "feat: add INSET token to lexer"
```

---

### Task 4: Parser inset grammar rule

**Files:**
- Modify: `procedural_buildings/parsing/Parser.py`

- [ ] **Step 1: Add OpInset to imports**

Change the import line to include `OpInset`:
```python
from ..Ops import (Op, OpSplit, OpRepeat, OpRepeatN, OpComp, OpColour,
                   OpRotate, OpResizeScope, OpScale, OpTranslate, OpPrimitive,
                   OpNil, OpSetParams, OpInset)
```

- [ ] **Step 2: Add inset parser rule**

Add after the `OpNil()` rule:

```python
@_("INSET LPAR expr RPAR LCURL singleOp BAR singleOp RCURL")
def singleOp(self, p):
    return OpInset(p.expr, childOps=[p.singleOp0, p.singleOp1])
```

- [ ] **Step 3: Compile check**

Run: `python3 -m py_compile procedural_buildings/parsing/Parser.py`
Expected: no errors

- [ ] **Step 4: Commit**

```bash
git add procedural_buildings/parsing/Parser.py
git commit -m "feat: add inset grammar rule to parser"
```

---

### Task 5: New primitive OBJ files

**Files:**
- Create: `procedural_buildings/primitives/arch.obj`
- Create: `procedural_buildings/primitives/column.obj`
- Create: `procedural_buildings/primitives/balcony.obj`
- Create: `procedural_buildings/primitives/dormer.obj`
- Create: `procedural_buildings/primitives/pediment.obj`

Each OBJ file follows the existing convention: centered at origin, axis-aligned, positive z = up, vertices followed by faces. The rectangles in coordinates below are listed as vertex indices; adapt to actual `.obj` face syntax (`f 1 2 3 4`).

- [ ] **Step 1: Create arch.obj**

A 1x2 arched opening (0.5m radius arch):
```
v -0.5 0.0 0.0
v 0.5 0.0 0.0
v 0.5 2.0 0.0
v 0.0 2.5 0.0
v -0.5 2.0 0.0
f 1 2 3 4 5
```

- [ ] **Step 2: Create column.obj**

A simple 0.5m diameter, 3m tall cylindrical column (8-sided approximation):
```
v -0.25 -1.5 0.0
v -0.177 -0.177 -1.5
v 0.0 -0.25 -1.5
v 0.177 -0.177 -1.5
v 0.25 0.0 -1.5
v 0.177 0.177 -1.5
v 0.0 0.25 -1.5
v -0.177 0.177 -1.5
v -0.25 0.0 -1.5
v -0.177 -0.177 1.5
v 0.0 -0.25 1.5
v 0.177 -0.177 1.5
v 0.25 0.0 1.5
v 0.177 0.177 1.5
v 0.0 0.25 1.5
v -0.177 0.177 1.5
v 0.0 0.0 -1.5
v 0.0 0.0 1.5
f 1 5 4 3 2
f 1 2 7 6 17
f 1 6 9 8 7
f 1 8 5
f 2 3 11 10
f 3 4 12 11
f 4 5 13 12
f 5 1 9 14 13
f 1 2 10 16 9
f 2 7 15 10
f 7 8 16 15
f 8 9 16
f 10 11 18
f 11 12 18
f 12 13 18
f 13 14 18
f 14 15 18
f 15 16 18
f 16 10 18
```

- [ ] **Step 3: Create balcony.obj**

A 2x1 balcony slab with railing:
```
v -1.0 0.0 0.0
v 1.0 0.0 0.0
v 1.0 0.1 0.0
v -1.0 0.1 0.0
v -1.0 0.0 1.0
v 1.0 0.0 1.0
v 1.0 0.1 1.0
v -1.0 0.1 1.0
f 1 2 3 4
f 5 6 7 8
f 1 2 6 5
f 2 3 7 6
f 3 4 8 7
f 4 1 5 8
```

- [ ] **Step 4: Create dormer.obj**

A 1.5x1.5 dormer window with pitched roof:
```
v -0.75 0.0 0.0
v 0.75 0.0 0.0
v 0.75 1.0 0.0
v 0.0 1.5 0.0
v -0.75 1.0 0.0
v -0.75 0.0 1.0
v 0.75 0.0 1.0
v 0.75 1.0 1.0
v 0.0 1.5 1.0
v -0.75 1.0 1.0
f 1 2 3 4 5
f 6 10 9 8 7
f 1 2 7 6
f 2 3 8 7
f 3 4 9 8
f 4 5 10 9
f 5 1 6 10
```

- [ ] **Step 5: Create pediment.obj**

A 2m wide, 1m peak triangular pediment:
```
v -1.0 0.0 0.0
v 1.0 0.0 0.0
v 0.0 1.0 0.0
v -1.0 0.0 1.0
v 1.0 0.0 1.0
v 0.0 1.0 1.0
f 1 2 3
f 4 6 5
f 1 2 5 4
f 2 3 6 5
f 3 1 4 6
```

- [ ] **Step 6: Verify primitives load**

Run:
```python
python3 -c "from procedural_buildings.Primitive import basicPrims; print(basicPrims.keys())"
```
Expected: `dict_keys([..., 'arch', 'column', 'balcony', 'dormer', 'pediment'])`

- [ ] **Step 7: Commit**

```bash
git add procedural_buildings/primitives/
git commit -m "feat: add 5 architectural primitives (arch, column, balcony, dormer, pediment)"
```

---

### Task 6: Integration test — inset grammar

**Files:**
- Create: `grammars/inset_demo` (example grammar using inset)
- Run with existing tool

- [ ] **Step 1: Create inset_demo grammar**

```
plot --> split(y){~1 : base | ~5 : floors | ~1 : roof}
base --> I(rect)
roof --> I(pediment)
floors --> split(x){~1 : I(column) | ~4 : bay | ~1 : I(column) | ~4 : bay | ~1 : I(column)}
bay --> inset(0.3){I(rect) | I(window)}
```

- [ ] **Step 2: Generate building from grammar**

Run:
```bash
uv run --with sly --with numpy --with sympy python -m procedural_buildings -i grammars/inset_demo -o /tmp/inset_demo.obj
```
Expected: generates OBJ successfully. Inspect with a text editor — should show vertices grouped as `o rect`, `o window`, `o column`, etc.

- [ ] **Step 3: Verify nested inset**

Create `grammars/inset_nested`:
```
plot --> inset(0.3){I(rect) | inset(0.2){I(rect) | I(rect)}}
```

Run:
```bash
uv run --with sly --with numpy --with sympy python -m procedural_buildings -i grammars/inset_nested -o /tmp/inset_nested.obj
```
Expected: generates OBJ with nested panels (outer frame, inner frame, innermost rect).

- [ ] **Step 4: Commit**

```bash
git add grammars/inset_demo grammars/inset_nested
git commit -m "feat: add inset demo grammars"
```

---

### Task 7: Richer diversity example grammar

**Files:**
- Create: `grammars/facade_city`

- [ ] **Step 1: Create facade_city grammar**

```
N = randint(3, 8)
plot --> split(y){~1 : base | ~(N * 3) : floors(0) | ~1 : roof}
floors(i) :
  i < N : split(y){~3 : floor | ~0.5 : band | ~(N * 3) : floors(i + 1)} |
  i >= N : split(y){~3 : floor}
floor --> split(x){~1 : I(column) | ~4 : bay | ~1 : I(column) | ~4 : bay | ~1 : I(column)}
bay --> inset(0.3){I(rect) | I(window)}
band --> colour(0.8, 0.8, 0.8) I(rect)
base --> colour(0.4, 0.4, 0.4) I(rect)
roof --> I(pediment)
```

- [ ] **Step 2: Generate multiple buildings**

```bash
uv run --with sly --with numpy --with sympy python -m procedural_buildings -i grammars/facade_city -o /tmp/facade_city.obj -n 3 -d 3
```
Expected: 3 different buildings with varying floor counts, columns, and recessed windows.

- [ ] **Step 3: Commit**

```bash
git add grammars/facade_city
git commit -m "feat: add facade_city grammar demonstrating inset + diversity"
```

---

### Task 8: Final verification

- [ ] **Step 1: Lint check**

```bash
ruff check --output-format=concise
```
Expected: "All checks passed!"

- [ ] **Step 2: Format check**

```bash
ruff format --check
```
Expected: "24 files already formatted"

- [ ] **Step 3: Run all existing grammars**

```bash
for g in grammars/city grammars/nice_roofs grammars/colour_blue grammars/simple_repeat; do
  uv run --with sly --with numpy --with sympy python -m procedural_buildings -i "$g" -o /tmp/test.obj || echo "FAIL: $g"
done
```
Expected: all pass

- [ ] **Step 4: Clean temp files**

```bash
rm -f /tmp/inset_demo.obj /tmp/inset_nested.obj /tmp/facade_city.obj /tmp/test.obj
```
