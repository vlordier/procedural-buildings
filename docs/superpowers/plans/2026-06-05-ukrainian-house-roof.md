# Ukrainian Village House Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace placeholder houses in `grammars/site_layout` with Ukrainian village-style houses using parametric roofs

**Architecture:** One-line engine change to make scope dimensions available everywhere, then a new grammar definition composed from existing primitives (triangle, rect, door, window3, column) using S/T for parametric roof overhang and pitch.

**Tech Stack:** Python 3.12+, numpy, sympy, sly (existing project)

---

### Task 1: Engine change — pass scope_env to children

**Files:**
- Modify: `procedural_buildings/Ops.py:385`

- [ ] **Step 1: Make the change**

`OpChooseRuleWithPriority.run()` builds `scope_env` with `width`/`depth`/`height` for condition evaluation, but passes `env` to children. Change it to pass `scope_env` so those variables are available to all child operations:

```python
# Before (line 385):
child.run(context, scope, env)
# After:
child.run(context, scope, scope_env)
```

- [ ] **Step 2: Run existing tests/grammars to verify nothing broke**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config python -m procedural_buildings -i grammars/neighbor_facade -o /tmp/test.obj 2>&1
```
Expected: generates OBJ with no errors

- [ ] **Step 3: Commit**

```bash
git add procedural_buildings/Ops.py
git commit -m "fix: make width/depth/height available to all child operations"
```

---

### Task 2: Write the Ukrainian village house grammar

**Files:**
- Modify: `grammars/site_layout` (replace entire content)

- [ ] **Step 1: Write the new grammar**

Replace the entire `grammars/site_layout`:

```grammar
-- Parameters
pitch = 0.6
overhang = 0.12

-- Colours
thatchR = 0.55; thatchG = 0.40; thatchB = 0.25
wallR = 0.95; wallG = 0.92; wallB = 0.88
shutterR = 0.20; shutterG = 0.35; shutterB = 0.55
doorR = 0.20; doorG = 0.35; doorB = 0.55
bandR = 0.85; bandG = 0.70; bandB = 0.60
decorHeight = 0.05

-- Site layout
road --> colour(0.2, 0.2, 0.2){I(rect)}
path --> colour(0.3, 0.3, 0.3){I(rect)}
block --> split(y){~1 : road | ~20 : lots | ~1 : road}

lots --> split(x){
  ~(randint(4, 7)) : lot(0)
  | ~1 : path
  | ~(randint(5, 8)) : lot(1)
  | ~1 : path
  | ~(randint(4, 7)) : lot(2)
}

lot(n) : n == 0 -->
  colour(0.6, 0.5, 0.4){
    split(y){~1 : colour(0.3, 0.3, 0.3){I(rect)} | ~(randint(3, 6)) : tower(n)}
  }

lot(n) : n == 1 -->
  split(y){~1 : pathToHouse | ~(randint(2, 5)) : ukrHouse}

lot(n) : n == 2 -->
  split(y){~1 : pathToHouse | ~(randint(2, 5)) : ukrHouse}

pathToHouse -->
  split(x){
    ~1 : colour(0.3, 0.3, 0.3){I(rect)}
    | ~0.08 : colour(0.85, 0.85, 0.85){
        split(z){~0.4 : nil | ~0.6 : I(rect)}
      }
    | ~1 : colour(0.3, 0.3, 0.3){I(rect)}
  }

ukrHouse -->
  split(z){
    ~1 : walls
    | ~pitch * (1 + 2*overhang)/2 :
        colour(thatchR, thatchG, thatchB){roof}
  }

walls -->
  split(z){
    ~decorHeight : colour(bandR, bandG, bandB){
      S(~(1 + 2*overhang), ~(1 + 2*overhang), ~1){I(rect)}
    }
    | ~1 : comp(f){
        front : colour(wallR, wallG, wallB){frontWall}
        left  : colour(wallR, wallG, wallB){I(rect)}
        right : colour(wallR, wallG, wallB){I(rect)}
        back  : colour(wallR, wallG, wallB){I(rect)}
      }
  }

frontWall : width > 7 -->
  split(z){
    ~2.5 : split(x){
      ~1 : I(rect) | ~1.5 : door | ~1.5 : windowPair | ~1 : I(rect)
    }
    | ~1 : split(x){
      ~1 : I(rect) | ~1.5 : windowPair | ~1 : I(rect)
      | ~1.5 : windowPair | ~1 : I(rect)
    }
  }

frontWall -->
  split(z){
    ~2.5 : split(x){~1 : I(rect) | ~1.5 : door | ~1 : I(rect)}
    | ~1 : split(x){~1 : I(rect) | ~1.5 : windowPair | ~1 : I(rect)}
  }

windowPair --> split(x){~0.3 : shutter | ~1.5 : windowUnit | ~0.3 : shutter}
windowUnit --> opening(0.15){colour(0.9, 0.92, 0.95){I(rect)} | I(window3)}
shutter --> colour(shutterR, shutterG, shutterB){I(rect)}
door --> opening(0.1){colour(doorR, doorG, doorB){I(rect)} | I(door)}

roof -->
  S(width * (1 + 2*overhang), depth * (1 + 2*overhang),
    pitch * width * (1 + 2*overhang) / 2)
  T(-width * overhang, -depth * overhang, 0)
  {I(triangle)}

-- Tower kept for variety
tower(n) : n == 0 -->
  split(x){~1 : I(column) | ~4 : opening(0.3){I(rect) | I(window3)} | ~1 : I(column)}
tower(n) -->
  split(x){~1 : I(column) | ~4 : opening(0.3){I(rect) | I(window3)}
    | ~1 : I(column) | ~4 : opening(0.3){I(rect) | I(window3)} | ~1 : I(column)}
```

- [ ] **Step 2: Generate OBJ and verify it parses**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config python -m procedural_buildings -i grammars/site_layout -o outputs/site.obj -s 0,0,0,40,5,20 -R block 2>&1
```
Expected: no parse errors, OBJ written. Check output has houses with roofs (not just columns).

```bash
wc -l outputs/site.obj
```
Expected: > 2000 lines (more geometry than old site_layout)

- [ ] **Step 3: Generate GLB and open**

```bash
uv run --with numpy --with trimesh --with scipy python scripts/obj_to_glb_colored.py site 2>&1
open outputs/site_colored.glb
```

Visual check: houses should have white/cream walls, steep brown roofs with overhang, visible blue shutters, blue door.

- [ ] **Step 4: Commit**

```bash
git add grammars/site_layout
git commit -m "feat: Ukrainian village houses with parametric roofs in site_layout"
```