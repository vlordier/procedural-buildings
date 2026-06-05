# Batch 3: UV/Material/GLB Implementation Plan

> **For agentic workers:** Use subagent-driven-development.

**Goal:** Replace lossy .obj pipeline with direct GLB export with UVs and PBR materials.

**Architecture:** Wave 1 (C1 + C2 parallel), Wave 2 (C3 after both).

---

### Task C1: UV coordinates on all primitives

**Files:** All 21 `.obj` files in `procedural_buildings/primitives/`

- [ ] **Step 1: Check each primitive's current state**

```bash
cd /Users/vincent/Work/procedural-buildings
for f in procedural_buildings/primitives/*.obj; do
  has_uv=$(grep -c "^vt " "$f")
  echo "$(basename $f): $has_uv UVs"
done
```

- [ ] **Step 2: Add UVs to primitives without them**

For each primitive without UVs, add `vt` lines. Strategy:
- `rect.obj` (cube, 8 verts, 6 faces): already has partial UVs (6 entries for 6 faces). Faces reference vertex indices differently than UV indices. Fix to have proper per-face UVs with correct face references.
- Basic flat shapes (triangle, right_angle_triangle): planar XY map, 4 corners at (0,0), (1,0), (1,1), (0,1)
- 3D shapes (pyramid, dome, column, pediment, etc.): per-face planar UV or spherical projection

Format:
```obj
vt 0.0 0.0
vt 1.0 0.0
vt 1.0 1.0
vt 0.0 1.0
```

Face references use `v/vt/vn` triplets: `f 1/1/1 2/2/1 3/3/1`

- [ ] **Step 3: Update face data to reference VT indices**

Existing face data uses `f v1 v2 v3` (vertex-only). After adding UVs, faces must use `f v1/vt1 v2/vt2 v3/vt3`.

- [ ] **Step 4: Test**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/ -q 2>&1 | tail -5
```

Commit:
```bash
git add procedural_buildings/primitives/
git commit -m "feat: add UV coordinates to all primitives"
```

---

### Task C2: Material op + GeometryAccumulator

**Files:**
- Modify: `procedural_buildings/_names.py`, `Ops.py`, `Lexer.py`, `Parser.py`, `ContextObj.py`, `Primitive.py`
- Create: `procedural_buildings/GeometryAccumulator.py`, `procedural_buildings/materials.py`

- [ ] **Step 1: Add MATERIAL to OpName enum**

In `_names.py`, add `MATERIAL = "material"` to OpName.

- [ ] **Step 2: Add MATERIAL token to Lexer**

Add `MATERIAL` to the Lexer token set.

- [ ] **Step 3: Add parser rule**

```
MATERIAL LPAR IDENT RPAR LCURL op RCURL → OpMaterial
```

- [ ] **Step 4: Add OpMaterial to Ops.py**

```python
class OpMaterial(Op):
    opName = OpName.MATERIAL

    def run(self, context, scope, env):
        material_name = self.args.evaluate(env)[0]
        context.material(material_name)
        if self.childOps:
            self.childOps[0].run(context, scope, scope_env(env, scope))
```

- [ ] **Step 5: Add material tracking to ContextObj**

```python
# In __init__:
self.currentMaterial = None

# New method:
def material(self, name: str) -> None:
    self.currentMaterial = name

# In reset():
self.currentMaterial = None
```

- [ ] **Step 6: Extract UVs and normals from primitive parsing**

In `Primitive.__init__`, extract `vt` and `vn` lines into structured
arrays (`self.uvs`, `self.normals`) instead of lumping into otherData.

- [ ] **Step 7: Create `materials.py`**

```python
import gin


@gin.configurable
def material_presets(values=None):
    return values or {}


def get_material(name):
    presets = material_presets()
    return presets.get(name, {
        "base_color": [0.7, 0.7, 0.7, 1.0],
        "roughness": 0.5,
        "metallic": 0.0,
    })
```

- [ ] **Step 8: Create `GeometryAccumulator.py`**

```python
class GeometryAccumulator:
    def __init__(self):
        self.positions = []
        self.normals = []
        self.uvs = []
        self.indices = []
        self.material_names = []
        self.vertex_count = 0
        self.current_material = None

    def add_primitive(self, prim, scope):
        verts = scope.putVertsInScope(prim.verts, prim.boundingBox)
        base = self.vertex_count
        for v in verts:
            self.positions.append([float(v[0]), float(v[1]), float(v[2])])
        # Add normals if available
        if prim.normals:
            for n in prim.normals:
                self.normals.append([float(n[0]), float(n[1]), float(n[2])])
        # Add UVs if available
        if prim.uvs:
            for uv in prim.uvs:
                self.uvs.append([float(uv[0]), float(uv[1])])
        # Add face indices
        for face in prim.face_indices:
            tri = [base + idx - 1 for idx in face]
            self.indices.append(tri)
            if self.current_material:
                self.material_names.append(self.current_material)
        self.vertex_count += len(verts)

    def reset(self):
        self.positions = []
        self.normals = []
        self.uvs = []
        self.indices = []
        self.material_names = []
        self.vertex_count = 0

    def material(self, name):
        self.current_material = name
```

- [ ] **Step 9: Test**

```bash
cd /Users/vincent/Work/procedural-buildings
ruff check --fix procedural_buildings/ && ruff format procedural_buildings/
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/ -q 2>&1 | tail -5
```

Commit:
```bash
git add -A
git commit -m "feat: add material() op, GeometryAccumulator, material presets via gin"
```

---

### Task C3: Direct GLB export

**Files:**
- Create: `procedural_buildings/GltfWriter.py`, `configs/materials_basic.gin`
- Modify: `procedural_buildings/__main__.py`

- [ ] **Step 1: Create `GltfWriter.py`**

A class that takes a `GeometryAccumulator` and writes a binary `.glb` file.
Key requirements:
- Binary glTF 2.0 format (single `.glb` file)
- Interleaved vertex buffer: position (vec3f) + normal (vec3f) + UV (vec2f)
- Index buffer: triangle indices (uint32)
- One PBR material per unique material name used in the scene
- Uses `material_presets()` from `materials.py` to get PBR properties

- [ ] **Step 2: Wire into CLI**

In `__main__.py`, detect `.glb` extension:
```python
if outFile.endswith(".glb"):
    # Use GeometryAccumulator + GltfWriter instead of ContextOBJ
    from .GeometryAccumulator import GeometryAccumulator
    from .GltfWriter import GltfWriter
    acc = GeometryAccumulator()
    # Run grammar, populate accumulator
    ...
    GltfWriter(acc).write(outFile)
else:
    # Existing .obj path
    p.grammarToManyObjs(inFile, startRule, startScope, n, sep, outFile)
```

Integrating with Processor: Processor needs a mode where it populates
a GeometryAccumulator instead of a ContextOBJ.

- [ ] **Step 3: Create default material config**

`configs/materials_basic.gin`:
```gin
material_presets.values = {
    "stone": {"base_color": [0.60, 0.55, 0.50], "roughness": 0.8, "metallic": 0.0},
    "brick": {"base_color": [0.70, 0.30, 0.20], "roughness": 0.9, "metallic": 0.0},
    "roof_tile": {"base_color": [0.40, 0.25, 0.20], "roughness": 0.6, "metallic": 0.0},
    "wood": {"base_color": [0.55, 0.35, 0.15], "roughness": 0.7, "metallic": 0.0},
    "glass": {"base_color": [0.60, 0.70, 0.80], "roughness": 0.1, "metallic": 0.0},
    "plaster": {"base_color": [0.85, 0.82, 0.78], "roughness": 0.5, "metallic": 0.0},
}
```

- [ ] **Step 4: Test GLB output**

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config python -m procedural_buildings \
  -i grammars/material_building \
  -o /tmp/test.glb \
  -s 0,0,0,8,8,12 \
  -g configs/materials_basic.gin
file /tmp/test.glb
```

Expected: `file` command shows `data` (binary glTF format).

- [ ] **Step 5: Full test suite**

```bash
cd /Users/vincent/Work/procedural-buildings
ruff check --fix procedural_buildings/ scripts/ && ruff format procedural_buildings/ scripts/
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/ -q 2>&1 | tail -5
```

Commit:
```bash
git add -A
git commit -m "feat: direct GLB export with PBR materials and UVs"
```