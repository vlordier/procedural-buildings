# Cluster 3: Grammar Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Clean up the grammar directory: archive 16 broken/duplicate grammars, add READMEs, update test xfail lists.

**Architecture:** 4 items. 3.1 (archive) and 3.4 (update tests) are coupled (archive first, then update xfails). 3.2 and 3.3 (READMEs) are independent and can be parallel.

---

### Task 3.1: Archive 16 grammars to `_archive/`

- [ ] **Step 1: Create `grammars/_archive/`**

```bash
cd /Users/vincent/Work/procedural-buildings
mkdir -p grammars/_archive
```

- [ ] **Step 2: Move 16 grammars**

```bash
cd /Users/vincent/Work/procedural-buildings
git mv grammars/also_nice_house grammars/_archive/
git mv grammars/amazing_house grammars/_archive/
git mv grammars/better_house grammars/_archive/
git mv grammars/cabin grammars/_archive/
git mv grammars/foo grammars/_archive/
git mv grammars/home grammars/_archive/
git mv grammars/home_new_grammar_style grammars/_archive/
git mv grammars/house_with_garage grammars/_archive/
git mv grammars/house_with_garage2 grammars/_archive/
git mv grammars/house_with_garage3 grammars/_archive/
git mv grammars/house_with_prims grammars/_archive/
git mv grammars/nice_house grammars/_archive/
git mv grammars/nice_roof_house grammars/_archive/
git mv grammars/nice_roofs_2 grammars/_archive/
git mv grammars/overlap grammars/_archive/
git mv grammars/window grammars/_archive/
```

- [ ] **Step 3: Verify**

```bash
cd /Users/vincent/Work/procedural-buildings
ls grammars/_archive/ | wc -l
```

Expected: 16

- [ ] **Step 4: Commit**

```bash
git add grammars/_archive/
git rm grammars/also_nice_house grammars/amazing_house grammars/better_house grammars/cabin grammars/foo grammars/home grammars/home_new_grammar_style grammars/house_with_garage grammars/house_with_garage2 grammars/house_with_garage3 grammars/house_with_prims grammars/nice_house grammars/nice_roof_house grammars/nice_roofs_2 grammars/overlap grammars/window
git commit -m "chore: archive 16 broken/duplicate grammars to grammars/_archive/"
```

---

### Task 3.2: Write grammars/README.md

- [ ] **Step 1: Create `grammars/README.md`**

```markdown
# Grammars

This directory contains grammar files for the procedural_buildings engine.
Each file is a shape grammar that describes one or more building types.

## Showcase grammars (the ones to try first)

| Grammar | Start rule | Description |
|---|---|---|
| `orthodox_church` | `plot` | White church with green roof and golden dome |
| `soviet_block` | `plot` | Parametric panel block (gin-config) |
| `european_townhouse` | `plot` | Narrow 3-story urban townhouse |
| `medieval_house` | `plot` | Half-timbered facade |
| `material_building` | `plot` | Gin-configurable material/pattern system |
| `warehouse_district` | `block` | Industrial block with gabled/sawtooth roofs |
| `modern_district` | `district` | Glass tower + apartment + mixed-use |
| `site_layout` | `block` | Village block with khata + barn + tower |
| `facade_city` | `plot` | Multi-building city with adaptive facades |

## Feature demo grammars

| Grammar | Feature |
|---|---|
| `opening_demo` | Window/door openings in walls |
| `inset_demo` | Inset/decorative panels |
| `gin_demo` | Gin-config integration |
| `neighbor_facade` | Adaptive facade using env conditions |

## Op test grammars (`op_tests/`)

Each file in this directory exercises a single engine feature:
`split`, `repeat`, `repeatN`, `comp`, `colour`, `priority`,
`conditions`, `rand`, `randint`, `prim`, `params`, `constants`.

These are auto-discovered and run by `tests/test_op_grammars.py`.

## Archive (`_archive/`)

Historical/experimental grammars kept for reference. Not actively maintained.

## How to add a new grammar

1. Create a file in `grammars/<name>` (no extension).
2. The default start rule is `plot`. If your grammar needs a different
   one, add an entry to `GRAMMAR_OVERRIDES` in `tests/test_grammars.py`.
3. Run `pytest tests/test_grammars.py::test_grammar_renders` to verify.
4. For gin-controlled parameters, create a config in `configs/`.
```

- [ ] **Step 2: Run tests to confirm nothing broke**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/ -q 2>&1 | tail -3
```

- [ ] **Step 3: Commit**

```bash
git add grammars/README.md
git commit -m "docs: add grammars/README.md with showcase directory"
```

---

### Task 3.3: Write configs/README.md

- [ ] **Step 1: Create `configs/README.md`**

```markdown
# Gin Configs

Grammar parameters (colours, sizes, counts) can be overridden at runtime
using [gin-config](https://github.com/google/gin-config) files.

## Usage

```bash
python -m procedural_buildings \
  -i grammars/material_building \
  -o outputs/checker.obj \
  -s 0,0,0,8,8,12 \
  -g configs/checker.gin
```

Or override inline without a file:

```bash
python -m procedural_buildings \
  -i grammars/material_building \
  -o outputs/custom.obj \
  -s 0,0,0,8,8,12 \
  -p 'grammar_var_overrides.values = {"wallPattern": 2, "wallR": 0.8}'
```

## Available configs

| Config | For grammar | Effect |
|---|---|---|
| `brick.gin` | `material_building` | Solid brick wall, dark roof |
| `nordic.gin` | `material_building` | White wall, blue horizontal stripe |
| `checker.gin` | `material_building` | Cream + brown checkerboard |
| `gradient.gin` | `material_building` | White-to-blue gradient |
| `soviet_9story.gin` | `soviet_block` | 9-story panel block |

## How to write a new config

```gin
grammar_var_overrides.values = {
    "wallPattern": 1,
    "wallR": 0.95,
    "wallG": 0.92,
    "wallB": 0.88,
    "stripeW": 0.1,
}
```

The variable names must match the `name = value` declarations in the
grammar file. All numeric types (int, float) are supported.
```

- [ ] **Step 2: Commit**

```bash
git add configs/README.md
git commit -m "docs: add configs/README.md with gin-config guide"
```

---

### Task 3.4: Update test_grammars.py xfail list

- [ ] **Step 1: Read current xfail list**

```bash
cd /Users/vincent/Work/procedural-buildings
grep -A 30 "XFAIL_GRAMMARS" tests/test_grammars.py
```

- [ ] **Step 2: Remove the 16 archived paths from XFAIL_GRAMMARS**

Edit `tests/test_grammars.py` to delete these entries:
- `"grammars/also_nice_house"`
- `"grammars/amazing_house"`
- `"grammars/better_house"`
- `"grammars/cabin"`
- `"grammars/foo"`
- `"grammars/home"`
- `"grammars/home_new_grammar_style"`
- `"grammars/house_with_garage"`
- `"grammars/house_with_garage2"`
- `"grammars/house_with_garage3"`
- `"grammars/house_with_prims"`
- `"grammars/nice_house"`
- `"grammars/nice_roof_house"`
- `"grammars/nice_roofs_2"`
- `"grammars/overlap"`
- `"grammars/window"`

- [ ] **Step 3: Run tests to verify xfail count dropped**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/ -q 2>&1 | tail -3
```

Expected: xfail count should drop from 29 to 13.

- [ ] **Step 4: Commit**

```bash
git add tests/test_grammars.py
git commit -m "test: remove archived grammars from XFAIL_GRAMMARS list"
```

---

### Task 3.5: Final verification

- [ ] **Step 1: Full test suite + lint**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/ -q 2>&1 | tail -3
ruff check --fix tests/ procedural_buildings/ scripts/
ruff format tests/ procedural_buildings/ scripts/
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/ -q 2>&1 | tail -3
```

- [ ] **Step 2: Commit formatting**

```bash
git add -A
git commit -m "style: ruff format after cluster 3 grammar cleanup"
```