import json
import os
import struct

from .GeometryAccumulator import GeometryAccumulator
from .materials import get_material

GLB_MAGIC = 0x46546C67
GLB_VERSION = 2
CHUNK_JSON = 0x4E4F534A
CHUNK_BIN = 0x004E4942

FLOAT_SIZE = 4


class GltfWriter:
    def __init__(self, accumulator: GeometryAccumulator):
        self.acc = accumulator

    def write(self, path: str):
        doc, bin_data = self._build()
        json_bytes = json.dumps(doc, separators=(",", ":")).encode("utf-8")
        json_padded = self._pad(json_bytes, 4)
        bin_padded = self._pad(bin_data, 4)

        length = 12 + 8 + len(json_padded) + 8 + len(bin_padded)
        with open(path, "wb") as f:
            f.write(struct.pack("<II", GLB_MAGIC, GLB_VERSION))
            f.write(struct.pack("<I", length))
            f.write(struct.pack("<II", len(json_padded), CHUNK_JSON))
            f.write(json_padded)
            f.write(struct.pack("<II", len(bin_padded), CHUNK_BIN))
            f.write(bin_padded)

    def write_gltf(self, path: str):
        """Write as separate .gltf JSON + .bin file (human-readable)."""
        doc, bin_data = self._build()
        bin_name = os.path.basename(path).rsplit(".", 1)[0] + ".bin"
        doc["buffers"][0]["uri"] = bin_name
        with open(path, "w") as f:
            json.dump(doc, f, indent=2)
        bin_path = path.rsplit(".", 1)[0] + ".bin"
        with open(bin_path, "wb") as f:
            f.write(bin_data)

    def _build(self):
        acc = self.acc
        vert_count = acc.vertex_count

        mat_names = list(dict.fromkeys(acc.material_names))

        groups: dict[str | None, list[int]] = {n: [] for n in mat_names}
        for idx, mat in zip(acc.indices, acc.material_names):
            if mat not in groups:
                groups[mat] = []
            groups[mat].append(idx)

        vert_stride = (3 + 3 + 2) * FLOAT_SIZE
        vert_data = bytearray()
        for i in range(vert_count):
            p = acc.positions[i]
            vert_data += struct.pack("<fff", p[0], p[1], p[2])
            if i < len(acc.normals):
                n = acc.normals[i]
                vert_data += struct.pack("<fff", n[0], n[1], n[2])
            else:
                vert_data += struct.pack("<fff", 0.0, 1.0, 0.0)
            if i < len(acc.uvs):
                uv = acc.uvs[i]
                vert_data += struct.pack("<ff", uv[0], uv[1])
            else:
                vert_data += struct.pack("<ff", 0.0, 0.0)

        index_data = bytearray()
        for mat in mat_names:
            for idx in groups[mat]:
                index_data += struct.pack("<I", idx)

        vert_size = len(vert_data)
        index_size = len(index_data)
        bin_data = bytes(vert_data + index_data)

        position_min = [
            min(p[0] for p in acc.positions),
            min(p[1] for p in acc.positions),
            min(p[2] for p in acc.positions),
        ]
        position_max = [
            max(p[0] for p in acc.positions),
            max(p[1] for p in acc.positions),
            max(p[2] for p in acc.positions),
        ]

        accessor_pos = {
            "bufferView": 0,
            "componentType": 5126,
            "count": vert_count,
            "type": "VEC3",
            "min": position_min,
            "max": position_max,
        }
        accessor_norm = {
            "bufferView": 1,
            "componentType": 5126,
            "count": vert_count,
            "type": "VEC3",
        }
        accessor_uv = {
            "bufferView": 2,
            "componentType": 5126,
            "count": vert_count,
            "type": "VEC2",
        }

        buffer_views = [
            {"buffer": 0, "byteOffset": 0, "byteLength": vert_size, "byteStride": vert_stride},
            {"buffer": 0, "byteOffset": 0, "byteLength": vert_size, "byteStride": vert_stride},
            {"buffer": 0, "byteOffset": 0, "byteLength": vert_size, "byteStride": vert_stride},
            {"buffer": 0, "byteOffset": vert_size, "byteLength": index_size},
        ]

        materials = []
        for name in mat_names:
            bc = [0.7, 0.7, 0.7, 1.0]
            roughness = 0.5
            metallic = 0.0
            if name and name.startswith("col_") and hasattr(acc, "_colour_materials"):
                rgb = acc._colour_materials.get(name)
                if rgb:
                    bc = rgb + [1.0]
            elif name:
                preset = get_material(name)
                bc = preset.get("base_color", [0.7, 0.7, 0.7, 1.0])
                if len(bc) == 3:
                    bc = list(bc) + [1.0]
                roughness = preset.get("roughness", 0.5)
                metallic = preset.get("metallic", 0.0)
            materials.append({
                "name": name or "default",
                "pbrMetallicRoughness": {
                    "baseColorFactor": bc,
                    "roughnessFactor": roughness,
                    "metallicFactor": metallic,
                },
            })

        primitives = []
        for mi, name in enumerate(mat_names):
            tri_count = len(groups[name]) // 3
            if tri_count == 0:
                continue
            primitives.append({
                "attributes": {
                    "POSITION": 0,
                    "NORMAL": 1,
                    "TEXCOORD_0": 2,
                },
                "indices": 3,
                "material": mi,
            })

        if not primitives:
            primitives.append({
                "attributes": {"POSITION": 0, "NORMAL": 1, "TEXCOORD_0": 2},
                "indices": 3,
                "material": 0,
            })

        accessors = [accessor_pos, accessor_norm, accessor_uv, {
            "bufferView": 3,
            "componentType": 5125,
            "count": index_size // 4,
            "type": "SCALAR",
        }]

        doc = {
            "asset": {"version": "2.0", "generator": "procedural_buildings"},
            "scene": 0,
            "scenes": [{"nodes": [0]}],
            "nodes": [{"mesh": 0}],
            "meshes": [{"primitives": primitives}],
            "accessors": accessors,
            "bufferViews": buffer_views,
            "buffers": [{"byteLength": len(bin_data)}],
            "materials": materials,
        }

        return doc, bin_data

    @staticmethod
    def _pad(data: bytes, alignment: int) -> bytes:
        remainder = len(data) % alignment
        if remainder:
            data += b" " * (alignment - remainder)
        return data
