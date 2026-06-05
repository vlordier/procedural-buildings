# Cluster 4: Dev Tooling & Docs Implementation Plan

> **For agentic workers:** Use subagent-driven-development to implement task-by-task.

**Goal:** Make the project pleasant to work in: Makefile, architecture doc, README sync, how_to doc, type hints.

**Architecture:** All 5 items are independent — can be done in parallel.

---

### Task 4.1: Makefile

- [ ] **Step 1: Create `Makefile`**

```makefile
.PHONY: test lint example

test:
	uv run --with sly --with numpy --with sympy --with gin-config pytest tests/ -q

lint:
	ruff check procedural_buildings/ tests/ scripts/
	ruff format --check procedural_buildings/ tests/ scripts/

example:
	uv run --with sly --with numpy --with sympy --with gin-config python -m procedural_buildings \
		-i grammars/material_building \
		-o /tmp/example.obj \
		-s 0,0,0,8,8,12
	@echo "Written to /tmp/example.obj"

all: test lint example
```

- [ ] **Step 2: Verify**
```bash
cd /Users/vincent/Work/procedural-buildings
make test 2>&1 | tail -3
make lint 2>&1 | tail -3
make example 2>&1 | tail -3
```

- [ ] **Step 3: Commit**
```bash
git add Makefile
git commit -m "feat: add Makefile with test/lint/example targets"
```

---

### Task 4.2: ARCHITECTURE.md

- [ ] **Step 1: Create `docs/ARCHITECTURE.md`**

```markdown
# Architecture

## Data Flow

```
Grammar file (.grammar)
        │
        ▼
┌────────────────┐
│   Lexer        │  SLY-based tokeniser
│   Parser       │  SLY-based LALR(1) parser → rule dict
│   Checker      │  Resolves rule references, builds op graph
│   GrammarVars  │  Expression evaluation (sympy-backed)
└───────┬────────┘
        │ Op graph (Op tree)
        ▼
┌────────────────┐
│   Processor    │  Runs op.run(context, scope, env) recursively
│   Ops.py       │  16 Op subclasses (split, repeat, colour, etc.)
│   Scope.py     │  Scope propagation, transforms, splits
│   ContextObj   │  Accumulates primitives and renders to .obj
└───────┬────────┘
        │ .obj file
        ▼
┌────────────────┐
│   Viewer       │  Pyglet-based 3D viewer (procedural_buildings/view.py)
│   obj_to_glb.py│  OBJ → glTF/GLB conversion
└────────────────┘

## Reverse Path

```
.obj file
        │
        ▼
┌────────────────┐
│   ObjReader    │  Reads .obj, extracts vertex data per primitive
│   BoxSplitter  │  Spatial splitter: boxes → Container tree → Op tree
│   simplify     │  Merges duplicate ops, produces minimal grammar
│   toGrammarText│  Serialises op tree back to grammar text
└───────┬────────┘
        │ Grammar file
        ▼
```

## Key Abstractions

- **Scope**: Position + rotation + size of a shape in 3D space
- **Op**: A shape-rewriting operation (split, repeat, colour, etc.)
- **Args**: Type-aware argument container with sympy expression evaluation
- **ContextObj**: Accumulator that collects primitives and writes .obj
- **Box**: A bounding box in 3D, linked to a primitive op
- **Container**: A spatial partition of boxes along an axis

## Environment (env dict)

The env dict flows through the op tree and carries:
- width/depth/height of the current scope
- neighbour info (left_width, right_width, etc.) for adaptive rules
- User-set variables via OpSetParams
- Grammar variable overrides via gin-config
```

- [ ] **Step 2: Commit**
```bash
git add docs/ARCHITECTURE.md
git commit -m "docs: add ARCHITECTURE.md with data flow diagram"
```

---

### Task 4.3: README sync

- [ ] **Step 1: Read current README**
```bash
cd /Users/vincent/Work/procedural-buildings
cat README.md
```

- [ ] **Step 2: Rewrite `README.md`**

```markdown
# Procedural Buildings

A shape-grammar engine for procedural generation of 3D building models.
Grammars describe buildings as nested splits, repeats, transforms, and
colours. Output is standard .obj format, viewable with any 3D viewer.

## Quick start

```bash
# Install dependencies
uv sync

# Render a grammar to .obj
uv run --with sly --with numpy --with sympy --with gin-config python -m procedural_buildings \
  -i grammars/material_building \
  -o outputs/example.obj \
  -s 0,0,0,8,8,12

# View it
uv run --with sly --with numpy --with sympy --with gin-config python -m procedural_buildings.view outputs/example.obj

# Validate a grammar (no output file needed)
uv run --with sly --with numpy --with sympy --with gin-config python -m procedural_buildings \
  --validate -i grammars/orthodox_church

# Reproducible build with a seed
uv run --with sly --with numpy --with sympy --with gin-config python -m procedural_buildings \
  -i grammars/modern_district \
  -o outputs/district.obj \
  -s 0,0,0,40,10,30 --seed 42
```

## Showcase grammars

| Grammar | Start rule | Example command |
|---|---|---|
| `orthodox_church` | `plot` | `-i grammars/orthodox_church -s 0,0,0,8,8,14` |
| `soviet_block` | `plot` | `-i grammars/soviet_block -s 0,0,0,12,8,15` |
| `european_townhouse` | `plot` | `-i grammars/european_townhouse -s 0,0,0,8,8,12` |
| `medieval_house` | `plot` | `-i grammars/medieval_house -s 0,0,0,10,8,10` |
| `material_building` | `plot` | `-i grammars/material_building -s 0,0,0,8,8,12` |
| `warehouse_district` | `block` | `-i grammars/warehouse_district -s 0,0,0,40,10,20` |
| `modern_district` | `district` | `-i grammars/modern_district -s 0,0,0,40,10,30` |
| `site_layout` | `block` | `-i grammars/site_layout -s 0,0,0,40,10,20` |

## Gin-config integration

Grammar parameters can be overridden at runtime:

```bash
uv run --with sly --with numpy --with sympy --with gin-config python -m procedural_buildings \
  -i grammars/material_building \
  -o outputs/checker.obj \
  -s 0,0,0,8,8,12 \
  -g configs/checker.gin
```

See `configs/README.md` for available configs and how to write new ones.

## CLI reference

```
-i <grammar_file>       Input grammar
-o <output.obj>         Output .obj file
-s <x1,y1,z1,x2,y2,z2>  Start scope (default 0,0,0,8,8,12)
-R <rule>                Start rule (default "plot")
--seed <N>               Reproducible random seed
--validate               Parse + simplify only, no output
-g <config.gin>          Gin config file
-p <bindings>            Gin inline bindings
-r                       Reverse path: .obj → grammar
-n <count>               Number of buildings (for multi-building)
-d <distance>            Separation between buildings
-f                       One .obj file per building
-v                       Verbose logging
```

## Running tests

```bash
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/
```

## Project structure

- `procedural_buildings/` — Engine source (Ops, Scope, Lexer, Parser, Processor, etc.)
- `grammars/` — Shape grammar files (see grammars/README.md)
- `configs/` — Gin-config parameter files (see configs/README.md)
- `tests/` — Pytest test suite
- `primitives/` — Primitive .obj files (rect, triangle, dome, etc.)
- `scripts/` — Utility scripts (update golden hashes, .obj → .glb)
- `docs/` — Documentation

## License

MIT
```

- [ ] **Step 3: Commit**
```bash
git add README.md
git commit -m "docs: rewrite README with current grammars, gin-config, CLI reference"
```

---

### Task 4.4: Move how_to doc

- [ ] **Step 1: Read current file**
```bash
cd /Users/vincent/Work/procedural-buildings
cat procedural_buildings/how_to_add_a_new_operation.txt
```

- [ ] **Step 2: Create `docs/how_to_add_a_new_operation.md`**

```markdown
# How to Add a New Operation

## 1. Add the op class to `Ops.py`

Create a new subclass of `Op`. Follow the pattern of existing ops:

```python
class OpMyNewOp(Op):
    opName = "my_new_op"

    def run(self, context, scope, env):
        # 1. Evaluate args
        # 2. Modify scope if needed
        # 3. Call scope_env(env, scope) for child env
        # 4. Run children
        for child in self.childOps:
            child.run(context, new_scope, scope_env(env, new_scope))
```

## 2. Add a parser rule in `Parser.py`

Add a grammar production for the new op. Follow the pattern of existing
production rules. The parser handles the `OPNAME(...){...}` syntax.

## 3. Add the keyword to `Lexer.py`

If the op name isn't already a token, add it to the lexer's token list.

## 4. Add a test grammar in `grammars/op_tests/`

Create a minimal grammar that exercises the new op:

```grammar
plot --> my_new_op(1, 2, 3){I(rect)}
```

## 5. Wire the test grammar into pytest

Add an entry to `tests/test_op_grammars.py` or verify the auto-discover
picks it up.

## 6. Add a unit test

Add a test to `tests/test_ops.py` following the existing pattern:

```python
def test_my_new_op_runs():
    scope = Scope.freshScope(...)
    env = {"width": 8, "depth": 8, "height": 12}
    op = OpMyNewOp(...)
    ctx = ContextObj()
    op.run(ctx, scope, env)
```

## The scope_env contract

Every operation that modifies the scope MUST call `scope_env(env, scope)`
to inject width/depth/height into the child's environment. This function
is in `Ops.py`:

```python
def scope_env(env, scope):
    new_env = env.copy()
    new_env["width"] = scope.size[0]
    new_env["depth"] = scope.size[1]
    new_env["height"] = scope.size[2]
    return new_env
```

If the op passes its scope to children, it MUST call `scope_env` and pass
the result. This is what makes `width`, `depth`, `height`, and neighbour
info available in grammar conditions.

## 7. Run the full test suite

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/
```
```

- [ ] **Step 3: Delete old .txt and new .md**
```bash
cd /Users/vincent/Work/procedural-buildings
git rm procedural_buildings/how_to_add_a_new_operation.txt
git add docs/how_to_add_a_new_operation.md
git commit -m "docs: move how_to_add doc to docs/ as .md with scope_env contract and test step"
```

---

### Task 4.5: Type hints on public surface

- [ ] **Step 1: Add basic type annotations to production files**

For each file, add type hints to public method signatures. Do NOT change
behavior. Just add `: type` and `-> type` annotations.

**`procedural_buildings/Scope.py`:**
- `freshScope(pos: np.ndarray, size: np.ndarray) -> Scope` — static
- `translate(self, v: np.ndarray) -> Scope`
- `rotate(self, axis: str, th: float) -> Scope`
- `resize(self, newSize: np.ndarray) -> Scope`
- `scale(self, factor: float) -> Scope`
- `split(self, axis: str, splitSizes: tuple) -> list`
- `repeat(self, axis: str, size: float) -> list`
- `repeatN(self, axis: str, n: int) -> list`
- `inset(self, amount: float) -> tuple`
- `opening(self, depth: float) -> tuple`
- `comp(self, face: str) -> Scope`

**`procedural_buildings/Ops.py`:**
- `Op.__init__(self, *args, **kwargs)`
- `Op.run(self, context, scope, env)`
- `Op.simplify(self, other) -> Op | None`
- `Op.combineMany(ops: list) -> Op` — static
- `Args.__init__(self, *args, perChildArgs=())`
- `Args.evaluate(self, env: dict)`
- `Args.combineArgs(a: Args, b: Args) -> Args | None` — static

**`procedural_buildings/ContextObj.py`:**
- `__init__(self)`
- `colour(self, col: tuple, scope: Scope)`
- `addPrim(self, prim, scope: Scope)`
- `writeObj(self, fname: str)`
- `setColourAlpha(self, newAlpha: float)`

**`procedural_buildings/Primitive.py`:**
- `__init__(self, lines: list)`

**`procedural_buildings/ObjReader.py`:**
- `objToOpGraph(fname: str, primDict: dict | None) -> tuple`

**`procedural_buildings/BoxSplitter.py`:**
- `Box.__init__(self, bounds, prim, colour=None)`
- `Container.__init__(self, axis: int)`
- `boxesToOp(boxes: list, initialContainer: Container)`

Use `from __future__ import annotations` at the top of each file to
avoid circular import issues.

- [ ] **Step 2: Verify no behavior change**
```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/ -q 2>&1 | tail -3
```

- [ ] **Step 3: Commit**
```bash
git add procedural_buildings/Scope.py procedural_buildings/Ops.py procedural_buildings/ContextObj.py procedural_buildings/Primitive.py procedural_buildings/ObjReader.py procedural_buildings/BoxSplitter.py
git commit -m "style: add type hints to public surface of Scope, Op, Args, ContextObj, Primitive, ObjReader, BoxSplitter"
```

---

### Task 4.6: Final verification

- [ ] **Step 1: Full test suite + lint**
```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/ -q 2>&1 | tail -3
ruff check --fix procedural_buildings/ tests/
ruff format procedural_buildings/ tests/
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/ -q 2>&1 | tail -3
```

- [ ] **Step 2: Commit formatting**
```bash
git add -A
git commit -m "style: ruff format cluster 4 changes"
```