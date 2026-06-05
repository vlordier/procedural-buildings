# C2 — Material Op + GeometryAccumulator

## Goal
New grammar op `material(name)` that sets the current material key,
and a `GeometryAccumulator` class that builds vertex buffers in memory
(positions, normals, UVs, material index per face) for direct export.

## Material op

### Parser/Lexer
- Add `MATERIAL` token to Lexer
- Add parser rule: `MATERIAL LPAR IDENT RPAR LCURL op RCURL`
- Add `OpMaterial` to `Ops.py`:

```python
class OpMaterial(Op):
    opName = OpName.MATERIAL

    def run(self, context, scope, env):
        material_name = self.args.evaluate(env)[0]
        context.material(material_name)
        if self.childOps:
            self.childOps[0].run(context, scope, scope_env(env, scope))
```

### Add to _names.py
```python
class OpName(StrEnum):
    ...
    MATERIAL = "material"
```

### Gin-configurable presets
In `procedural_buildings/materials.py`:
```python
import gin

@gin.configurable
def material_presets(values=None):
    return values or {}

def get_material(name):
    presets = material_presets()
    return presets.get(name, {"base_color": [0.7, 0.7, 0.7], "roughness": 0.5, "metallic": 0.0})
```

## Material tracking in Context

### ContextObj changes
Add material tracking alongside currentColour:
- `self.currentMaterial = None`
- `def material(self, name): self.currentMaterial = name`
- `reset()` clears both

### GeometryAccumulator (new class)
```python
class GeometryAccumulator:
    """Builds vertex buffers for direct GLB export.
    Accumulates positions, normals, UVs, and material index per face."""
    
    def __init__(self):
        self.positions = []  # flat list of [x,y,z, x,y,z, ...]
        self.normals = []    # flat list of [nx,ny,nz, ...]
        self.uvs = []        # flat list of [u,v, u,v, ...]
        self.indices = []    # triangle indices into the vertex arrays
        self.material_indices = []  # one per triangle (or per primitive)
        self.current_material = None
    
    def add_primitive(self, prim, scope, material_name):
        """Transform primitive vertices by scope, append to buffers."""
        # Get transformed verts
        verts = scope.putVertsInScope(prim.verts, prim.boundingBox)
        # Get UVs from prim.otherData
        uvs = prim.uvs  # parsed vt entries
        # Get normals from prim.otherData
        normals = prim.normals  # parsed vn entries
        # Append to buffers, track material index
        ...
    
    def to_gltf_dict(self):
        """Return a dict suitable for json.dumps as glTF."""
        ...
```

## Primitive changes
Add `self.uvs` and `self.normals` to `Primitive.__init__`, parsed from
the `vt` and `vn` lines in the `.obj` file. Currently these are lumped
into `self.otherData` as raw text — extract them into structured arrays.

## Testing
```python
def test_material_op_sets_material():
    scope = Scope.freshScope(...)
    ctx = ContextObj()
    op = OpMaterial(perChildArgs=("stone",), childOps=[OpPrimitive("rect")])
    op.run(ctx, scope, env)
    assert ctx.currentMaterial == "stone"
```