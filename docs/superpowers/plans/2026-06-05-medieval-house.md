# Medieval Half-Timbered House Implementation Plan

**Goal:** Create `grammars/medieval_house` — a European medieval half-timbered house

**Architecture:** Single grammar file using split + I(rect) with alternating cream and dark brown panels to simulate timber framing. Uses the existing S/T/I(triangle) roof pattern with clay-tile colour.

---

### Task 1: Create medieval_house grammar

**Files:**
- Create: `grammars/medieval_house`

- [ ] **Step 1: Write the grammar file**

```grammar
whiteR = 0.90
whiteG = 0.85
whiteB = 0.80
timberR = 0.30
timberG = 0.20
timberB = 0.15
roofR = 0.65
roofG = 0.35
roofB = 0.20
glassR = 0.60
glassG = 0.70
glassB = 0.80
pitch = 0.65
plot --> S(~1, ~1, 8){medievalHouse}
medievalHouse --> split(z){~5 : walls | ~3 : roof}
walls --> comp(f){front : colour(whiteR, whiteG, whiteB){facade} | left : I(rect) | right : I(rect) | back : I(rect)}
facade --> split(z){~2.5 : split(x){~0.3 : timber | ~2 : panelWin | ~0.3 : timber | ~2 : doorPanel | ~0.3 : timber} | ~2.5 : split(x){~0.3 : timber | ~2 : panelWin | ~0.3 : timber | ~2 : panelWin | ~0.3 : timber}}
panelWin --> colour(whiteR, whiteG, whiteB){split(x){~0.15 : timber | ~1.7 : windowUnit | ~0.15 : timber}}
windowUnit --> split(x){~0.15 : timber | ~1.4 : colour(glassR, glassG, glassB){I(rect)} | ~0.15 : timber}
doorPanel --> colour(whiteR, whiteG, whiteB){split(x){~0.15 : timber | ~1.7 : door | ~0.15 : timber}}
door --> colour(timberR, timberG, timberB){I(rect)}
timber --> colour(timberR, timberG, timberB){I(rect)}
roof --> colour(roofR, roofG, roofB){S(width * 1.1, depth * 1.1, pitch * width * 1.1 / 2){T(-width * 0.05, -depth * 0.05, 0){I(triangle)}}}
```

- [ ] **Step 2: Generate OBJ and verify**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config python -m procedural_buildings -i grammars/medieval_house -o outputs/medieval.obj -s 0,0,0,8,10,8 2>&1
```
Expected: no errors, OBJ generated

- [ ] **Step 3: Generate GLB**

```bash
uv run --with numpy --with trimesh --with scipy python scripts/obj_to_glb_colored.py medieval 2>&1
```

- [ ] **Step 4: Commit**

```bash
git add grammars/medieval_house
git commit -m "feat: add medieval half-timbered house grammar"
```