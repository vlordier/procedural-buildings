# Barn Outbuilding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a wooden barn/shed outbuilding behind each Ukrainian house in the site layout

**Architecture:** Add barn parameters and rules to `grammars/site_layout`, modify `lot(n)` rules to add a third split section for the barn behind the house

**Tech Stack:** Python 3.12+, existing procedural_buildings project

---

### Task 1: Add barn rules to site_layout

**Files:**
- Modify: `grammars/site_layout`

- [ ] **Step 1: Add barn parameters after existing colours**

```grammar
barnPitch = 0.4
barnOverhang = 0.08
barnHeight = 0.6
woodR = 0.55
woodG = 0.45
woodB = 0.35
barnRoofR = 0.40
barnRoofG = 0.30
barnRoofB = 0.20
```

- [ ] **Step 2: Modify lot rules to add barn section**

Change:
```grammar
lot(n) : n == 1 --> split(y){~1 : pathToHouse | ~(randint(2, 5)) : ukrainianHouse}
lot(n) : n == 2 --> split(y){~1 : pathToHouse | ~(randint(2, 5)) : ukrainianHouse}
```
To:
```grammar
lot(n) : n == 1 --> split(y){~1 : pathToHouse | ~(randint(2, 5)) : ukrainianHouse | ~(randint(1, 2)) : barn}
lot(n) : n == 2 --> split(y){~1 : pathToHouse | ~(randint(2, 5)) : ukrainianHouse | ~(randint(1, 2)) : barn}
```

- [ ] **Step 3: Add barn rules at the end, before tower rules**

```grammar
barn --> split(z){~barnHeight : colour(woodR, woodG, woodB){barnWalls} | ~(barnPitch * (1 + 2*barnOverhang)/2) : colour(barnRoofR, barnRoofG, barnRoofB){barnRoof}}
barnWalls --> comp(f){front : colour(woodR, woodG, woodB){split(x){~1 : I(rect) | ~2 : opening(0.1){colour(woodR, woodG, woodB){I(rect)} | nil} | ~1 : I(rect)}} | left : colour(woodR, woodG, woodB){I(rect)} | right : colour(woodR, woodG, woodB){I(rect)} | back : colour(woodR, woodG, woodB){I(rect)}}
barnRoof --> S(width * (1 + 2*barnOverhang), depth * (1 + 2*barnOverhang), barnPitch * width * (1 + 2*barnOverhang) / 2){T(-width * barnOverhang, -depth * barnOverhang, 0){I(triangle)}}
```

- [ ] **Step 4: Generate OBJ and verify**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config python -m procedural_buildings -i grammars/site_layout -o outputs/site.obj -s 0,0,0,40,5,20 -R block 2>&1
```
Expected: no errors, OBJ generated. Line count should increase from ~11,687.

- [ ] **Step 5: Generate GLB**

```bash
uv run --with numpy --with trimesh --with scipy python scripts/obj_to_glb_colored.py site 2>&1
```
Expected: GLB generated with more verts/faces than before.

- [ ] **Step 6: Commit**

```bash
git add grammars/site_layout
git commit -m "feat: add wooden barn outbuilding behind each house"
```
