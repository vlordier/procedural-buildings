#!/usr/bin/env python3
"""Convert OBJ (with colour annotations) to GLB with material colours.

Usage:
    python scripts/obj_to_glb.py input.obj output.glb
"""

import json
import os
import struct
import sys

import numpy as np

try:
    import pygltflib
except ImportError:
    pygltflib = None


def _parse_obj(path):
    """Parse OBJ with colour annotations into per-object geometry groups.

    Returns a list of dicts: {name, colour (r,g,b) | None, vertices, normals, indices}
    """
    verts = []
    objects = []
    current_obj = None
    current_colour = None
    current_name = None

    with open(path) as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("#"):
            i += 1
            continue
        parts = line.split()
        if not parts:
            i += 1
            continue

        if parts[0] == "o":
            if current_obj is not None:
                objects.append(current_obj)

            colour_marker = "# colour("
            if "#" in line and colour_marker in line:
                colour_part = line.split(colour_marker, 1)[1].rstrip(")")
                current_colour = tuple(float(x) for x in colour_part.split(","))
            else:
                current_colour = None

            current_name = " ".join(parts[1:]).split(" #")[0].strip()
            current_obj = {
                "name": current_name,
                "colour": current_colour,
                "vertices": [],
                "faces": [],
            }
        elif parts[0] == "v" and len(parts) >= 4:
            verts.append([float(x) for x in parts[1:4]])
        elif parts[0] == "vn" and len(parts) >= 4:
            pass
        elif parts[0] == "f":
            if current_obj is None:
                current_obj = {"name": "object", "colour": None, "vertices": [], "faces": []}
            indices = []
            for p in parts[1:]:
                v_idx = int(p.split("/")[0]) - 1
                indices.append(v_idx)
            for j in range(1, len(indices) - 1):
                current_obj["faces"].append((indices[0], indices[j], indices[j + 1]))
        i += 1

    if current_obj is not None:
        objects.append(current_obj)

    if not objects:
        return []

    verts_arr = np.array(verts, dtype=np.float32)
    n_verts = len(verts_arr)

    norm_accum = np.zeros((n_verts, 3), dtype=np.float32)
    face_count = np.zeros(n_verts, dtype=np.int32)
    for obj in objects:
        for tri in obj["faces"]:
            v0 = verts_arr[tri[0]]
            v1 = verts_arr[tri[1]]
            v2 = verts_arr[tri[2]]
            n = np.cross(v1 - v0, v2 - v0)
            norm_len = np.linalg.norm(n)
            if norm_len > 0:
                n /= norm_len
            for idx in tri:
                norm_accum[idx] += n
                face_count[idx] += 1

    for i in range(n_verts):
        if face_count[i] > 0:
            norm_accum[i] /= face_count[i]
            norm_len = np.linalg.norm(norm_accum[i])
            if norm_len > 0:
                norm_accum[i] /= norm_len

    result = []
    for obj in objects:
        if not obj["faces"]:
            continue
        obj_verts = []
        obj_norms = []
        obj_indices = []
        used = {}
        next_idx = 0
        for tri in obj["faces"]:
            for idx in tri:
                if idx not in used:
                    used[idx] = next_idx
                    obj_verts.append(verts_arr[idx])
                    obj_norms.append(norm_accum[idx])
                    next_idx += 1
                obj_indices.append(used[idx])

        result.append({
            "name": obj["name"],
            "colour": obj["colour"],
            "vertices": np.array(obj_verts, dtype=np.float32),
            "normals": np.array(obj_norms, dtype=np.float32),
            "indices": np.array(obj_indices, dtype=np.uint32),
        })

    return result


def _write_glb_pygltflib(groups, output_path):
    """Write GLB using pygltflib."""
    gltf = pygltflib.GLTF2()
    gltf.asset = pygltflib.Asset(version="2.0", generator="obj_to_glb")

    all_positions = []
    all_normals = []
    all_indices = []
    mesh_primitives = []
    node_children = []
    material_indices = []
    index_offset = 0

    for group in groups:
        positions = group["vertices"]
        normals = group["normals"]
        indices = group["indices"]

        if len(positions) == 0:
            continue

        col = group["colour"]
        if col is not None:
            mat_idx = len(gltf.materials)
            pbr = pygltflib.PbrMetallicRoughness(
                baseColorFactor=[col[0], col[1], col[2], 1.0],
                metallicFactor=0.0,
                roughnessFactor=0.8,
            )
            gltf.materials.append(
                pygltflib.Material(
                    name=group["name"],
                    pbrMetallicRoughness=pbr,
                )
            )
        else:
            mat_idx = len(gltf.materials)
            pbr = pygltflib.PbrMetallicRoughness(
                baseColorFactor=[0.8, 0.8, 0.8, 1.0],
                metallicFactor=0.0,
                roughnessFactor=0.8,
            )
            gltf.materials.append(
                pygltflib.Material(
                    name=group["name"],
                    pbrMetallicRoughness=pbr,
                )
            )

        prim = pygltflib.Primitive(
            attributes=pygltflib.Attributes(
                POSITION=len(all_positions),
                NORMAL=len(all_normals),
            ),
            indices=len(all_indices),
            material=mat_idx,
        )
        mesh_primitives.append(prim)
        material_indices.append(mat_idx)
        node_children.append(len(gltf.meshes))

        all_positions.append(positions)
        all_normals.append(normals)
        adjusted = indices + index_offset
        all_indices.append(adjusted)
        index_offset += len(positions)

        mesh = pygltflib.Mesh(primitives=[prim], name=group["name"])
        gltf.meshes.append(mesh)

    if not all_positions:
        return

    combined_positions = np.vstack(all_positions) if len(all_positions) > 1 else all_positions[0]
    combined_normals = np.vstack(all_normals) if len(all_normals) > 1 else all_normals[0]
    combined_indices = np.hstack(all_indices) if len(all_indices) > 1 else all_indices[0]

    binary_blob = combined_positions.tobytes() + combined_normals.tobytes() + combined_indices.tobytes()

    pos_byte_len = combined_positions.nbytes
    norm_byte_len = combined_normals.nbytes
    index_byte_len = combined_indices.nbytes

    pos_offset = 0
    norm_offset = pos_byte_len
    index_offset = pos_byte_len + norm_byte_len

    gltf.buffers.append(pygltflib.Buffer(byteLength=len(binary_blob)))
    gltf.bufferViews.append(
        pygltflib.BufferView(
            buffer=0,
            byteOffset=pos_offset,
            byteLength=pos_byte_len,
            target=pygltflib.ARRAY_BUFFER,
        )
    )
    gltf.bufferViews.append(
        pygltflib.BufferView(
            buffer=0,
            byteOffset=norm_offset,
            byteLength=norm_byte_len,
            target=pygltflib.ARRAY_BUFFER,
        )
    )
    gltf.bufferViews.append(
        pygltflib.BufferView(
            buffer=0,
            byteOffset=index_offset,
            byteLength=index_byte_len,
            target=pygltflib.ELEMENT_ARRAY_BUFFER,
        )
    )

    gltf.accessors.append(
        pygltflib.Accessor(
            bufferView=0,
            componentType=pygltflib.FLOAT,
            count=len(combined_positions),
            type=pygltflib.VEC3,
            min=combined_positions.min(axis=0).tolist(),
            max=combined_positions.max(axis=0).tolist(),
        )
    )
    gltf.accessors.append(
        pygltflib.Accessor(
            bufferView=1,
            componentType=pygltflib.FLOAT,
            count=len(combined_normals),
            type=pygltflib.VEC3,
        )
    )
    gltf.accessors.append(
        pygltflib.Accessor(
            bufferView=2,
            componentType=pygltflib.UNSIGNED_INT,
            count=len(combined_indices),
            type=pygltflib.SCALAR,
        )
    )

    for i, _prim in enumerate(mesh_primitives):
        gltf.meshes[i].primitives[0].attributes.POSITION = 0
        gltf.meshes[i].primitives[0].attributes.NORMAL = 1
        mesh_primitives[i].indices = 2

    scene = pygltflib.Scene(nodes=list(range(len(gltf.meshes))))
    gltf.scenes.append(scene)

    gltf.set_binary_blob(binary_blob)
    gltf.save(output_path)


def _write_glb_raw(groups, output_path):
    """Write GLB binary without pygltflib."""
    positions_list = []
    normals_list = []
    indices_list = []
    meshes = []
    index_offset = 0

    for group in groups:
        if len(group["vertices"]) == 0:
            continue
        col = group["colour"] or (0.8, 0.8, 0.8)
        adjusted = group["indices"] + index_offset
        positions_list.append(group["vertices"])
        normals_list.append(group["normals"])
        indices_list.append(adjusted)
        meshes.append({"indices": adjusted, "colour": col})
        index_offset += len(group["vertices"])

    if not positions_list:
        return

    all_pos = np.vstack(positions_list) if len(positions_list) > 1 else positions_list[0]
    all_norm = np.vstack(normals_list) if len(normals_list) > 1 else normals_list[0]
    all_idx = np.hstack(indices_list) if len(indices_list) > 1 else indices_list[0]

    pos_data = all_pos.tobytes()
    norm_data = all_norm.tobytes()
    idx_data = all_idx.tobytes()
    bin_data = pos_data + norm_data + idx_data

    pos_byte_len = len(pos_data)
    norm_byte_len = len(norm_data)
    idx_byte_len = len(idx_data)

    min_pos = all_pos.min(axis=0).tolist()
    max_pos = all_pos.max(axis=0).tolist()

    materials = []
    for m in meshes:
        materials.append(m["colour"])

    json_obj = {
        "asset": {"version": "2.0", "generator": "obj_to_glb"},
        "scene": 0,
        "scenes": [{"nodes": list(range(len(meshes)))}],
        "nodes": [{"mesh": i} for i in range(len(meshes))],
        "meshes": [],
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5126,
                "count": len(all_pos),
                "type": "VEC3",
                "min": min_pos,
                "max": max_pos,
            },
            {
                "bufferView": 1,
                "componentType": 5126,
                "count": len(all_norm),
                "type": "VEC3",
            },
            {
                "bufferView": 2,
                "componentType": 5125,
                "count": len(all_idx),
                "type": "SCALAR",
            },
        ],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": pos_byte_len, "target": 34962},
            {"buffer": 0, "byteOffset": pos_byte_len, "byteLength": norm_byte_len, "target": 34962},
            {"buffer": 0, "byteOffset": pos_byte_len + norm_byte_len, "byteLength": idx_byte_len, "target": 34963},
        ],
        "buffers": [{"byteLength": len(bin_data)}],
        "materials": [],
    }

    for i, col in enumerate(materials):
        json_obj["materials"].append({
            "pbrMetallicRoughness": {
                "baseColorFactor": [col[0], col[1], col[2], 1.0],
                "metallicFactor": 0.0,
                "roughnessFactor": 0.8,
            },
        })
        json_obj["meshes"].append({
            "primitives": [
                {
                    "attributes": {"POSITION": 0, "NORMAL": 1},
                    "indices": 2,
                    "material": i,
                }
            ],
        })

    json_str = json.dumps(json_obj, separators=(",", ":"))
    while len(json_str) % 4 != 0:
        json_str += " "
    json_bytes = json_str.encode("utf-8")

    json_pad = (4 - len(json_bytes) % 4) % 4
    json_bytes += b" " * json_pad

    bin_pad = (4 - len(bin_data) % 4) % 4
    bin_data += b"\x00" * bin_pad

    total_length = 12 + 8 + len(json_bytes) + 8 + len(bin_data)

    with open(output_path, "wb") as f:
        f.write(struct.pack("<I", 0x46546C67))
        f.write(struct.pack("<I", 2))
        f.write(struct.pack("<I", total_length))
        f.write(struct.pack("<I", len(json_bytes)))
        f.write(struct.pack("<I", 0x4E4F534A))
        f.write(json_bytes)
        f.write(struct.pack("<I", len(bin_data)))
        f.write(struct.pack("<I", 0x004E4942))
        f.write(bin_data)

    print(f"Wrote {output_path} ({total_length} bytes)")


def main():

    if len(sys.argv) < 2:
        print("Usage: python scripts/obj_to_glb.py <input.obj> [output.glb]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) >= 3 else os.path.splitext(input_path)[0] + ".glb"

    if not os.path.exists(input_path):
        print(f"Input file not found: {input_path}")
        sys.exit(1)

    groups = _parse_obj(input_path)
    if not groups:
        print(f"No geometry found in {input_path}")
        sys.exit(1)

    n_verts = sum(len(g["vertices"]) for g in groups)
    n_tris = sum(len(g["indices"]) for g in groups) // 3
    print(f"Parsed {len(groups)} objects, {n_verts} vertices, {n_tris} triangles")

    if pygltflib is not None:
        _write_glb_pygltflib(groups, output_path)
    else:
        _write_glb_raw(groups, output_path)

    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
