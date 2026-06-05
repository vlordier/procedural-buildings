# C3 — Direct GLB Export

## Goal
Write a `GltfWriter` that takes a `GeometryAccumulator` and produces
a binary `.glb` file with PBR materials, UVs, and correct vertex data.
No .obj round-trip.

## Approach
Write glTF 2.0 binary format directly. glTF is JSON + binary buffer in a
single `.glb` file. The structure:

```
┌─────────────────┐
│ Header (12B)    │  magic, version, length
├─────────────────┤
│ JSON chunk      │  scenes, nodes, meshes, materials, accessors,
│                 │  bufferViews, samplers, textures
├─────────────────┤
│ BIN chunk       │  vertex buffer (interleaved positions, normals, UVs)
│                 │  index buffer (triangle indices)
└─────────────────┘
```

## File: `procedural_buildings/GltfWriter.py`

```python
import json
import struct

GLB_MAGIC = 0x46546C67  # "glTF"
GLB_VERSION = 2
GLB_JSON = 0x4E4F534A
GLB_BIN = 0x004E4942


class GltfWriter:
    def __init__(self, accumulator: GeometryAccumulator):
        self.acc = accumulator
    
    def write(self, path: str):
        """Write .glb file from accumulated geometry."""
        # Build glTF JSON
        doc = self._build_json()
        json_bytes = json.dumps(doc, separators=(",", ":")).encode("utf-8")
        # Pad to 4-byte alignment
        json_padded = self._pad(json_bytes, 4)
        
        # Build binary buffer (interleaved vertex data + indices)
        bin_data = self._build_binary()
        bin_padded = self._pad(bin_data, 4)
        
        # Write header + chunks
        total_length = 12 + 8 + len(json_padded) + 8 + len(bin_padded)
        with open(path, "wb") as f:
            # Header
            f.write(struct.pack("<II", GLB_MAGIC, GLB_VERSION))
            # JSON chunk
            f.write(struct.pack("<II", len(json_padded), GLB_JSON))
            f.write(json_padded)
            # BIN chunk
            f.write(struct.pack("<II", len(bin_padded), GLB_BIN))
            f.write(bin_padded)
    
    def _build_json(self) -> dict:
        """Build the glTF JSON document."""
        acc = self.acc
        
        # Material definitions
        materials = []
        for mat_name in acc.material_names:
            preset = get_material(mat_name)
            materials.append({
                "pbrMetallicRoughness": {
                    "baseColorFactor": preset.get("base_color", [0.7, 0.7, 0.7, 1.0]),
                    "roughnessFactor": preset.get("roughness", 0.5),
                    "metallicFactor": preset.get("metallic", 0.0),
                }
            })
        
        # Accessors for positions, normals, uvs, indices
        accessors = [...]
        buffer_views = [...]
        
        return {
            "asset": {"version": "2.0", "generator": "procedural_buildings"},
            "scene": 0,
            "scenes": [{"nodes": [0]}],
            "nodes": [{"mesh": 0}],
            "meshes": [{
                "primitives": [{
                    "attributes": {
                        "POSITION": 0,
                        "NORMAL": 1,
                        "TEXCOORD_0": 2,
                    },
                    "indices": 3,
                    "material": mat_idx,
                }]
            }],
            "accessors": accessors,
            "bufferViews": buffer_views,
            "buffers": [{"uri": "data:", "byteLength": len(bin_data)}],
            "materials": materials,
        }
    
    def _build_binary(self) -> bytes:
        """Build interleaved vertex buffer + index buffer."""
        acc = self.acc
        buf = bytearray()
        # Interleaved: position (3f) + normal (3f) + uv (2f) per vertex
        for i in range(acc.vertex_count):
            buf += struct.pack("<fff", *acc.positions[i])
            buf += struct.pack("<fff", *acc.normals[i])
            buf += struct.pack("<ff", *acc.uvs[i])
        # Triangle indices
        for tri in acc.indices:
            buf += struct.pack("<III", *tri)
        return bytes(buf)
    
    def _pad(self, data: bytes, alignment: int) -> bytes:
        remainder = len(data) % alignment
        if remainder:
            data += b" " * (alignment - remainder)
        return data
```

## CLI integration
Add `.glb` detection to `__main__.py`: if `outFile` ends with `.glb`,
use `GltfWriter` instead of `ContextOBJ`.

## Preset configs
Create `configs/materials_basic.gin`:
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

## Testing
```python
def test_glb_writes_valid_file(tmp_path):
    acc = GeometryAccumulator()
    # Add a simple triangle with UVs
    ...
    writer = GltfWriter(acc)
    path = str(tmp_path / "test.glb")
    writer.write(path)
    assert os.path.getsize(path) > 0
    # Optionally validate with pygltflib or manual parse
```

## Out of scope
- Multiple meshes/primitives per file (single mesh per GLB for now)
- Animations, skins, morph targets
- Draco mesh compression