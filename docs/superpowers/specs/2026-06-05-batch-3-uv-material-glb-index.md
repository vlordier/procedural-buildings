# Batch 3: UV + Material + GLB Pipeline — Index

**Goal:** Replace the .obj-based output pipeline with a direct GLB exporter
that produces textured, PBR-material assets ready for any 3D engine.

**Architecture:** 3 items. C1 (primitives UVs) and C2 (engine track) are
independent. C3 (GLB export) depends on both.

## Items

| # | Item | Files | Effort |
|---|---|---|---|
| C1 | UVs on all primitives | `procedural_buildings/primitives/*.obj` | Low |
| C2 | Material op + GeometryAccumulator | `_names.py`, `Ops.py`, `Lexer.py`, `Parser.py`, `GeometryAccumulator.py` | Medium |
| C3 | Direct GLB export | `GltfWriter.py`, `scripts/`, `configs/` | Medium |

## Material presets via gin-config

Materials are defined in `.gin` files and overridable at runtime:

```gin
material_presets.values = {
    "stone": {"base_color": [0.60, 0.55, 0.50], "roughness": 0.8, "metallic": 0.0},
    "roof_tile": {"base_color": [0.40, 0.25, 0.20], "roughness": 0.6, "metallic": 0.0},
    "glass": {"base_color": [0.60, 0.70, 0.80], "roughness": 0.1, "metallic": 0.0, "transmission": 0.9},
}
```

The `material(name)` grammar op looks up presets by name. GLB export writes
one PBR material per unique name used.

## Pipeline before/after

Before: Grammar → Op tree → ContextOBJ → .obj → obj_to_glb.py → .glb (lossy)
After:  Grammar → Op tree → GeometryAccumulator → GltfWriter → .glb (direct)

`ContextOBJ` is kept for .obj export (debugging + reverse path).

## Acceptance

- All 21 primitives have valid `vt` entries
- `material("stone"){I(rect)}` in a grammar sets the material slot
- `python -m procedural_buildings -i grammar -o out.glb` produces a .glb
  with UV coordinates and PBR materials
- glTF Validator or Three.js can load the output
- Material presets are overridable via gin-config