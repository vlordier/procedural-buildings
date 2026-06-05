# Warehouse District Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create grammars/warehouse_district with brick warehouses using gabled and sawtooth roofs

**Architecture:** New grammar file reusing the same S/T/I(triangle) roof pattern as houses, plus I(right_angle_triangle) for sawtooth teeth

**Tech Stack:** Python 3.12+, existing procedural_buildings project

---

### Task 1: Create warehouse_district grammar

**Files:**
- Create: `grammars/warehouse_district`

- [ ] **Step 1: Write the grammar file**

Create `grammars/warehouse_district`:

```grammar
brickR = 0.70
brickG = 0.30
brickB = 0.20
roofR = 0.30
roofG = 0.25
roofB = 0.20
glassR = 0.60
glassG = 0.70
glassB = 0.80
wallHeight = 8
roofPitch = 0.5
roofOverhang = 0.10
block --> split(y){~1 : road | ~30 : lots | ~1 : road}
road --> colour(0.2, 0.2, 0.2){I(rect)}
lots --> split(x){~(randint(6, 10)) : warehouseLot | ~0.5 : path | ~(randint(6, 10)) : warehouseLot | ~0.5 : path | ~(randint(6, 10)) : warehouseLot}
path --> colour(0.3, 0.3, 0.3){I(rect)}
warehouseLot --> split(y){~1 : truckBay | ~(randint(4, 8)) : warehouse}
truckBay --> colour(0.2, 0.2, 0.2){I(rect)}
warehouse --> split(z){~wallHeight : colour(brickR, brickG, brickB){warehouseWalls} | ~(roofPitch * (1 + 2*roofOverhang)/2) : warehouseRoof}
warehouseWalls --> comp(f){front : colour(brickR, brickG, brickB){split(x){~1 : I(rect) | ~3 : opening(0.3){colour(brickR, brickG, brickB){I(rect)} | nil} | ~1 : I(rect) | ~3 : opening(0.3){colour(brickR, brickG, brickB){I(rect)} | nil} | ~1 : I(rect)}} | left : colour(brickR, brickG, brickB){I(rect)} | right : colour(brickR, brickG, brickB){I(rect)} | back : colour(brickR, brickG, brickB){I(rect)}}
warehouseRoof --> gabledWarehouseRoof : 1
warehouseRoof --> sawtoothRoof : 1
gabledWarehouseRoof --> colour(roofR, roofG, roofB){S(width * (1 + 2*roofOverhang), depth * (1 + 2*roofOverhang), roofPitch * width * (1 + 2*roofOverhang) / 2){T(-width * roofOverhang, -depth * roofOverhang, 0){I(triangle)}}}
sawtoothRoof --> colour(roofR, roofG, roofB){repeatN(x, 4){sawtoothTooth}}
sawtoothTooth --> split(x){~0.08 : colour(glassR, glassG, glassB){I(rect)} | ~1 : I(right_angle_triangle)}
```

- [ ] **Step 2: Generate OBJ and verify**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config python -m procedural_buildings -i grammars/warehouse_district -o outputs/wardist.obj -s 0,0,0,40,10,20 2>&1
```
Expected: no errors, OBJ generated

- [ ] **Step 3: Generate GLB**

```bash
uv run --with numpy --with trimesh --with scipy python scripts/obj_to_glb_colored.py wardist 2>&1
```
Expected: GLB generated with mixed roof types

- [ ] **Step 4: Commit**

```bash
git add grammars/warehouse_district
git commit -m "feat: add warehouse district with gabled and sawtooth roofs"
```