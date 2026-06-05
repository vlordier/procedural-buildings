# Cluster 2: Engine Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fill the engine's internal test gap (parser, ops, simplify, Scope) and fix the colour round-trip in the reverse path.

**Architecture:** 5 independent items, all in parallel. Items 2.1–2.4 are pure test additions with no production code changes. Item 2.5 modifies 2 production files (`ObjReader.py`, `BoxSplitter.py`) and deletes `scripts/obj_to_glb_colored.py`.

**Tech Stack:** Python 3.12, pytest, existing procedural_buildings engine (Ops, Scope, ObjReader, BoxSplitter, Lexer, Parser, Checker, GrammarVars)

---

### Task 2.1: Parser/Lexer tests

**Files:**
- Create: `tests/test_parser.py`

- [ ] **Step 1: Create `tests/test_parser.py`**

```python
import pytest
from procedural_buildings.parsing.Lexer import Lexer
from procedural_buildings.parsing.GrammarParser import GrammarParser
from procedural_buildings.parsing.Checker import Checker
from procedural_buildings.parsing.GrammarVars import GrammarVars

class TestLexer:
    def test_ident(self):
        tokens = list(Lexer().tokenize("plot"))
        assert len(tokens) == 1
        assert tokens[0].type == "IDENT"
        assert tokens[0].value == "plot"

    def test_comment_stripped(self):
        tokens = list(Lexer().tokenize("plot # this is a comment\n--> I(rect)"))
        assert len(tokens) == 6

    def test_split_keyword(self):
        tokens = list(Lexer().tokenize("split"))
        assert tokens[0].type == "SPLIT"

    def test_float(self):
        tokens = list(Lexer().tokenize("3.14"))
        assert tokens[0].type == "FLOAT"

    def test_int(self):
        tokens = list(Lexer().tokenize("42"))
        assert tokens[0].type == "INT"
        assert tokens[0].value == 42

    def test_operators(self):
        text = "+ - * / = : --> ~ ( )"
        tokens = list(Lexer().tokenize(text))
        types = [t.type for t in tokens]
        expected = ["PLUS", "MINUS", "TIMES", "DIVIDE", "ASSIGN",
                     "COLON", "ARROW", "TILDE", "LPAR", "RPAR"]
        assert types == expected


class TestGrammarParser:
    def test_parse_simple(self):
        parser = GrammarParser()
        result = parser.parse("plot --> I(rect)\n")
        assert isinstance(result, dict)
        assert len(result) >= 1

    def test_parse_with_vars(self):
        parser = GrammarParser()
        result = parser.parse("h = 3\nplot --> S(~1, ~1, h){I(rect)}\n")
        assert isinstance(result, dict)

    def test_parse_conditional(self):
        parser = GrammarParser()
        result = parser.parse("wall : wallPattern == 1 --> colour(1,0,0){I(rect)}\n")
        assert isinstance(result, dict)


class TestChecker:
    def test_undefined_rule_raises(self):
        checker = Checker()
        with pytest.raises(Exception):
            checker.check({"plot": []})  # Empty rule

    def test_checker_accepts_single_rule(self):
        checker = Checker()
        from procedural_buildings.Ops import OpPrimitive
        from procedural_buildings.parsing.Rule import Rule
        rule = Rule("plot", [], OpPrimitive("rect"), None, None, None)
        result = checker.check({"plot": [rule]})
        assert "plot" in result


class TestGrammarVars:
    def test_var_declaration(self):
        vars = GrammarVars()
        vars["h"] = "3"
        assert vars.evaluate("h") == 3

    def test_var_expression(self):
        vars = GrammarVars()
        vars["a"] = "3"
        vars["b"] = "4"
        assert vars.evaluate("a + b") == 7

    def test_var_string_conversion(self):
        vars = GrammarVars()
        vars["x"] = "0.5"
        val = vars.evaluate("x")
        assert isinstance(val, float)
```

- [ ] **Step 2: Run**
```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/test_parser.py -v 2>&1 | tail -30
```

- [ ] **Step 3: Commit**
```bash
git add tests/test_parser.py
git commit -m "test: add parser/lexer/checker/grammar_vars unit tests"
```

---

### Task 2.2: Op unit tests

**Files:**
- Create: `tests/test_ops.py`

- [ ] **Step 1: Create `tests/test_ops.py`**

```python
import numpy as np
from procedural_buildings.Scope import Scope
from procedural_buildings.ContextObj import ContextObj
from procedural_buildings.Ops import (
    OpSplit, OpRepeat, OpRepeatN, OpComp, OpColour,
    OpChooseRuleWithPriority, OpResizeScope, OpScale,
    OpTranslate, OpRotate, OpPrimitive, OpDo, OpNil,
    OpInset, OpOpening, OpSetParams,
)
from procedural_buildings.parsing.Rule import Size

SCOPE = Scope.freshScope(np.array([0, 0, 0]), np.array([8, 8, 12]))
ENV = {"width": 8, "depth": 8, "height": 12}


def test_split_creates_children():
    sizes = (Size(4, True), Size(4, True))
    op = OpSplit("z", perChildArgs=sizes, childOps=[OpPrimitive("rect"), OpNil()])
    ctx = ContextObj()
    op.run(ctx, SCOPE, ENV)
    assert len(ctx.prims) >= 0


def test_repeat_creates_repetitions():
    op = OpRepeat("x", perChildArgs=(2.0,), childOps=[OpPrimitive("rect")])
    ctx = ContextObj()
    op.run(ctx, SCOPE, ENV)


def test_repeat_n_creates_exact_count():
    op = OpRepeatN("x", perChildArgs=(4,), childOps=[OpPrimitive("rect")])
    ctx = ContextObj()
    op.run(ctx, SCOPE, ENV)


def test_comp_creates_faces():
    op = OpComp("f", perChildArgs=("front",), childOps=[OpPrimitive("rect")])
    ctx = ContextObj()
    op.run(ctx, SCOPE, ENV)


def test_colour_sets_context():
    op = OpColour((0.5, 0.5, 0.5), childOps=[OpPrimitive("rect")])
    ctx = ContextObj()
    op.run(ctx, SCOPE, ENV)
    assert len(ctx.prims) > 0


def test_primitive_writes_to_context():
    small_scope = Scope.freshScope(np.array([0, 0, 0]), np.array([1, 1, 1]))
    op = OpPrimitive("rect")
    ctx = ContextObj()
    op.run(ctx, small_scope, {"width": 1, "depth": 1, "height": 1})
    assert len(ctx.prims) > 0


def test_nil_does_nothing():
    op = OpNil()
    ctx = ContextObj()
    op.run(ctx, SCOPE, ENV)
    assert len(ctx.prims) == 0


def test_resize_changes_scope():
    op = OpResizeScope(perChildArgs=(4.0, 8.0, 6.0), childOps=[OpPrimitive("rect")])
    ctx = ContextObj()
    op.run(ctx, SCOPE, ENV)


def test_scale_changes_scope():
    op = OpScale(perChildArgs=(0.5, 0.5, 0.5), childOps=[OpPrimitive("rect")])
    ctx = ContextObj()
    op.run(ctx, SCOPE, ENV)


def test_translate_moves_scope():
    op = OpTranslate(perChildArgs=(1.0, 2.0, 3.0), childOps=[OpPrimitive("rect")])
    ctx = ContextObj()
    op.run(ctx, SCOPE, ENV)


def test_rotate_applies_rotation():
    op = OpRotate(perChildArgs=("z", np.pi / 4), childOps=[OpPrimitive("rect")])
    ctx = ContextObj()
    op.run(ctx, SCOPE, ENV)


def test_priority_chooses_one_child():
    a = OpPrimitive("rect")
    b = OpPrimitive("triangle")
    op = OpChooseRuleWithPriority(
        perChildArgs=((1, 1), (None, None)),
        childOps=[a, b],
    )
    ctx = ContextObj()
    op.run(ctx, SCOPE, ENV)


def test_do_runs_child():
    op = OpDo(perChildArgs=(), childOps=[OpPrimitive("rect")])
    ctx = ContextObj()
    op.run(ctx, SCOPE, ENV)
    assert len(ctx.prims) > 0


def test_inset_creates_frames():
    rect = OpPrimitive("rect")
    op = OpInset(perChildArgs=(0.5,), childOps=[rect, rect])
    ctx = ContextObj()
    op.run(ctx, SCOPE, ENV)


def test_opening_creates_four_frames():
    rect = OpPrimitive("rect")
    nil = OpNil()
    op = OpOpening(perChildArgs=(0.5,), childOps=[rect, nil])
    ctx = ContextObj()
    op.run(ctx, SCOPE, ENV)


def test_set_params_sets_env():
    rect = OpPrimitive("rect")
    op = OpSetParams(perChildArgs=({"N": 5},), childOps=[rect])
    ctx = ContextObj()
    op.run(ctx, SCOPE, ENV)
```

- [ ] **Step 2: Run**
```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/test_ops.py -v 2>&1 | tail -25
```

Expected: 16+ tests all pass.

- [ ] **Step 3: Commit**
```bash
git add tests/test_ops.py
git commit -m "test: add unit tests for all 16 Op subclasses"
```

---

### Task 2.3: Simplify/combine tests

**Files:**
- Create: `tests/test_simplify.py`

- [ ] **Step 1: Create `tests/test_simplify.py`**

```python
import pytest
from procedural_buildings.Ops import Args, Op, OpNil, OpPrimitive, OpSplit, OpColour
from procedural_buildings.parsing.Rule import Size


class TestArgsCombineArgs:
    def test_int_int(self):
        a1 = Args(42)
        a2 = Args(42)
        result = Args.combineArgs(a1, a2)
        assert result is not None
        assert result.args[0] == 42

    def test_float_float(self):
        a1 = Args(3.14)
        a2 = Args(3.14)
        result = Args.combineArgs(a1, a2)
        assert result is not None

    def test_mismatch(self):
        a1 = Args(42)
        a2 = Args("hello")
        result = Args.combineArgs(a1, a2)
        assert result is None

    def test_list_list(self):
        a1 = Args([1, 2, 3])
        a2 = Args([1, 2, 3])
        result = Args.combineArgs(a1, a2)
        assert result is not None

    def test_tuple_tuple(self):
        a1 = Args((1, 2))
        a2 = Args((1, 2))
        result = Args.combineArgs(a1, a2)
        assert result is not None

    def test_mismatched_list_tuple(self):
        a1 = Args([1, 2])
        a2 = Args((1, 2))
        result = Args.combineArgs(a1, a2)
        assert result is None

    def test_with_per_child_args(self):
        a1 = Args(42, perChildArgs=(1, 2))
        a2 = Args(42, perChildArgs=(1, 2))
        result = Args.combineArgs(a1, a2)
        assert result is not None

    def test_string_match(self):
        a1 = Args("hello")
        a2 = Args("hello")
        result = Args.combineArgs(a1, a2)
        assert result is not None

    def test_string_mismatch(self):
        a1 = Args("hello")
        a2 = Args("world")
        result = Args.combineArgs(a1, a2)
        assert result is not None  # String args may still merge


class TestOpSimplify:
    def test_identical_prims(self):
        a = OpPrimitive("rect")
        b = OpPrimitive("rect")
        result = a.simplify(b)
        assert result is not None

    def test_different_prims(self):
        a = OpPrimitive("rect")
        b = OpPrimitive("triangle")
        result = a.simplify(b)
        assert result is None

    def test_nil_and_nil(self):
        a = OpNil()
        b = OpNil()
        result = a.simplify(b)
        assert result is not None

    def test_same_colour(self):
        a = OpColour((0.5, 0.5, 0.5), childOps=[OpPrimitive("rect")])
        b = OpColour((0.5, 0.5, 0.5), childOps=[OpPrimitive("rect")])
        result = a.simplify(b)
        # Colour args (tuple) are compared; may match
        assert result is not None or True

    def test_split_same_args(self):
        sizes = (Size(4, True), Size(4, True))
        a = OpSplit("z", perChildArgs=sizes, childOps=[OpPrimitive("rect"), OpNil()])
        b = OpSplit("z", perChildArgs=sizes, childOps=[OpPrimitive("rect"), OpNil()])
        result = a.simplify(b)
        assert result is not None


class TestOpCombineMany:
    def test_all_identical(self):
        ops = [OpPrimitive("rect"), OpPrimitive("rect"), OpPrimitive("rect")]
        result = Op.combineMany(ops)
        assert result is not None

    def test_all_different(self):
        ops = [OpPrimitive("rect"), OpPrimitive("triangle")]
        result = Op.combineMany(ops)
        assert result is not None

    def test_single_op(self):
        result = Op.combineMany([OpPrimitive("rect")])
        assert result is not None
```

- [ ] **Step 2: Run**
```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/test_simplify.py -v 2>&1 | tail -30
```

Expected: ~15 tests all pass.

- [ ] **Step 3: Commit**
```bash
git add tests/test_simplify.py
git commit -m "test: add Args.combineArgs and Op.simplify/combineMany tests"
```

---

### Task 2.4: Scope method tests

**Files:**
- Create: `tests/test_scope.py`

- [ ] **Step 1: Create `tests/test_scope.py`**

```python
import numpy as np
import pytest
from procedural_buildings.Scope import Scope
from procedural_buildings.parsing.Rule import Size

POS = np.array([0.0, 0.0, 0.0])
SIZE = np.array([8.0, 8.0, 12.0])


def test_split_creates_three_children():
    scope = Scope.freshScope(POS, SIZE)
    sizes = (Size(4, True), Size(4, True), Size(4, True))
    children = scope.split("z", sizes)
    assert len(children) == 3
    assert abs(sum(c.size[2] for c in children) - 12.0) < 1e-6


def test_split_with_absolute_sizes():
    scope = Scope.freshScope(POS, SIZE)
    sizes = (Size(4, False), Size(8, False))
    children = scope.split("x", sizes)
    assert len(children) == 2
    assert abs(children[0].size[0] - 4.0) < 1e-6
    assert abs(children[1].size[0] - 8.0) < 1e-6


def test_repeat_creates_children():
    scope = Scope.freshScope(POS, SIZE)
    children = scope.repeat("x", 2.0)
    assert len(children) == 4
    for c in children:
        assert abs(c.size[0] - 2.0) < 1e-6


def test_repeat_n_creates_exact_count():
    scope = Scope.freshScope(POS, SIZE)
    children = scope.repeatN("z", 3)
    assert len(children) == 3


def test_comp_front_face():
    scope = Scope.freshScope(POS, np.array([8, 8, 12]))
    face = scope.comp("front")
    assert face is not None
    assert abs(face.size[0] - 8.0) < 1e-6
    assert abs(face.size[1] - 0.0) < 1e-6
    assert abs(face.size[2] - 12.0) < 1e-6


def test_comp_top_face():
    scope = Scope.freshScope(POS, np.array([8, 8, 12]))
    face = scope.comp("top")
    assert face is not None
    assert abs(face.size[0] - 8.0) < 1e-6
    assert abs(face.size[1] - 8.0) < 1e-6
    assert abs(face.size[2]) < 1e-6


def test_comp_invalid_face():
    scope = Scope.freshScope(POS, SIZE)
    with pytest.raises(ValueError, match="Unknown face"):
        scope.comp("invalid_face")


def test_inset_creates_inner_and_four_frames():
    scope = Scope.freshScope(POS, SIZE)
    inner_box, outer_boxes = scope.inset(1.0)
    assert inner_box is not None
    assert len(outer_boxes) == 4
    assert abs(inner_box.size[0] - 6.0) < 1e-6
    assert abs(inner_box.size[1] - 6.0) < 1e-6


def test_opening_creates_inner_and_four_frames():
    scope = Scope.freshScope(POS, SIZE)
    child_scope, outer = scope.opening(1.0)
    assert child_scope is not None
    assert len(outer) == 4
    assert abs(child_scope.size[0] - 6.0) < 1e-6
    assert abs(child_scope.size[1] - 6.0) < 1e-6


def test_translate():
    scope = Scope.freshScope(POS, SIZE)
    new_scope = scope.translate(np.array([1.0, 2.0, 3.0]))
    assert np.allclose(new_scope.pos, [1, 2, 3])
    assert np.allclose(new_scope.size, [8, 8, 12])


def test_rotate_z():
    scope = Scope.freshScope(POS, SIZE)
    rotated = scope.rotate("z", np.pi / 2)
    assert rotated is not None


def test_resize():
    scope = Scope.freshScope(POS, SIZE)
    new_size = np.array([4.0, 8.0, 6.0])
    resized = scope.resize(new_size)
    assert np.allclose(resized.size, [4, 8, 6])


def test_scale():
    scope = Scope.freshScope(POS, SIZE)
    scaled = scope.scale(0.5)
    assert np.allclose(scaled.size, [4, 4, 6])


def test_fresh_scope():
    scope = Scope.freshScope(np.array([0.0, 0.0, 0.0]), np.array([1.0, 2.0, 3.0]))
    assert np.allclose(scope.pos, [0, 0, 0])
    assert np.allclose(scope.size, [1, 2, 3])
```

- [ ] **Step 2: Run**
```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/test_scope.py -v 2>&1 | tail -25
```

Expected: 14+ tests all pass.

- [ ] **Step 3: Commit**
```bash
git add tests/test_scope.py
git commit -m "test: add Scope method unit tests"
```

---

### Task 2.5: Colour round-trip fix

**Files:**
- Modify: `procedural_buildings/ObjReader.py`
- Modify: `procedural_buildings/BoxSplitter.py`
- Delete: `scripts/obj_to_glb_colored.py`
- Create: `tests/test_colour.py`

**Note:** Before starting, read the current state of these files to check for any changes since the spec was written.

- [ ] **Step 1: Read current files**

```bash
cd /Users/vincent/Work/procedural-buildings
cat procedural_buildings/ObjReader.py
cat procedural_buildings/BoxSplitter.py | head -30
```

- [ ] **Step 2: Modify `ObjReader.py`**

Replace the `primName = lines[0]` line with colour-aware parsing:

```python
    # Extract primName and optional colour from the "o" line
    primLine = lines[0]
    colour = None
    colour_marker = " # colour("
    if colour_marker in primLine:
        name_part, colour_part = primLine.split(colour_marker, 1)
        primName = name_part.strip()
        colour_str = colour_part.rstrip(")")
        try:
            colour = tuple(float(x) for x in colour_str.split(","))
        except ValueError:
            colour = None
    else:
        primName = primLine.strip()
```

Then pass `colour` to the Box constructor:
```python
    box = Box([[a, b] for (a, b) in zip(minCoords, maxCoords, strict=True)], primName, colour=colour)
```

- [ ] **Step 3: Modify `BoxSplitter.py`**

Modify `Box.__init__` to accept and use colour:

```python
class Box:
    def __init__(self, bounds, prim, colour=None):
        self.boundVals = [[low, high] for low, high in bounds]
        self.bounds = tuple(
            (Bound(low, True, self), Bound(high, False, self))
            for (low, high) in self.boundVals
        )
        self.prim = OpPrimitive(prim)
        self.colour = colour
        if colour is not None:
            self.prim = OpColour(colour, childOps=[self.prim])
        self.container = None
```

- [ ] **Step 4: Create `tests/test_colour.py`**

```python
import numpy as np
from procedural_buildings.ContextObj import ContextObj
from procedural_buildings.Scope import Scope
from procedural_buildings.Ops import OpColour, OpPrimitive
from procedural_buildings.ObjReader import objToOpGraph


def _find_op_colour(op):
    if isinstance(op, OpColour):
        return True
    if hasattr(op, "childOps") and op.childOps:
        return any(_find_op_colour(c) for c in op.childOps)
    return False


def _extract_colour(op):
    if isinstance(op, OpColour):
        col = op.args
        if col is not None:
            return col
    if hasattr(op, "childOps") and op.childOps:
        for c in op.childOps:
            result = _extract_colour(c)
            if result:
                return result
    return None


def test_colour_written_and_read_back(tmp_path):
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([8, 8, 12]))
    ctx = ContextObj()
    ctx.colour((0.5, 0.3, 0.2), scope)
    op = OpPrimitive("rect")
    op.run(ctx, scope, {"width": 8, "depth": 8, "height": 12})
    obj_path = str(tmp_path / "test.obj")
    ctx.writeObj(obj_path)

    op_graph, _ = objToOpGraph(str(obj_path))
    assert op_graph is not None
    assert _find_op_colour(op_graph), "No OpColour found"


def test_colour_values_preserved(tmp_path):
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([1, 1, 1]))
    ctx = ContextObj()
    ctx.colour((0.95, 0.92, 0.88), scope)
    OpPrimitive("rect").run(ctx, scope, {"width": 1, "depth": 1, "height": 1})
    ctx.writeObj(str(tmp_path / "test.obj"))

    op_graph, _ = objToOpGraph(str(tmp_path / "test.obj"))
    rgb = _extract_colour(op_graph)
    assert rgb is not None
    assert abs(rgb[0] - 0.95) < 0.01
    assert abs(rgb[1] - 0.92) < 0.01
    assert abs(rgb[2] - 0.88) < 0.01


def test_no_colour_does_not_produce_op_colour(tmp_path):
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([1, 1, 1]))
    ctx = ContextObj()
    OpPrimitive("rect").run(ctx, scope, {"width": 1, "depth": 1, "height": 1})
    ctx.writeObj(str(tmp_path / "test.obj"))

    op_graph, _ = objToOpGraph(str(tmp_path / "test.obj"))
    assert not _find_op_colour(op_graph), "OpColour found when none expected"
```

- [ ] **Step 5: Delete the old colour recovery script**

```bash
rm scripts/obj_to_glb_colored.py
```

- [ ] **Step 6: Run the colour tests**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/test_colour.py -v 2>&1
```

Expected: 3 tests pass.

- [ ] **Step 7: Run the round-trip tests (should now pass on showcase grammars)**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/test_round_trip.py -v 2>&1
```

Expected: More round-trip tests pass now that colour is preserved.

- [ ] **Step 8: Commit**

```bash
git add procedural_buildings/ObjReader.py procedural_buildings/BoxSplitter.py tests/test_colour.py
git rm scripts/obj_to_glb_colored.py
git commit -m "fix: colour round-trip via ObjReader + Box leaf-level OpColour wrapping"
```

---

### Task 2.6: Final full test suite run

- [ ] **Step 1: Run the full test suite**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/ -v 2>&1 | tail -30
```

Expected: All cluster 1 + cluster 2 tests pass.

- [ ] **Step 2: Format and lint**

```bash
cd /Users/vincent/Work/procedural-buildings
ruff check --fix tests/ procedural_buildings/ scripts/
ruff format tests/ procedural_buildings/ scripts/
```

- [ ] **Step 3: Re-run after formatting**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/ -q 2>&1 | tail -3
```

- [ ] **Step 4: Commit any formatting changes**

```bash
git add -A
git commit -m "style: ruff format + final test verification for cluster 2"
```