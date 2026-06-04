import re
import sys

import numpy as np
import trimesh


def obj_to_colored_glb(obj_path, glb_path):
    with open(obj_path) as f:
        lines = f.readlines()

    verts = []
    faces = []
    face_colors = []
    current_color = [0.5, 0.5, 0.5]
    vert_offset = 0

    for line in lines:
        line = line.strip()
        if line.startswith("o "):
            m = re.search(r"# colour\(([\d.]+),([\d.]+),([\d.]+)\)", line)
            current_color = [float(m.group(1)), float(m.group(2)), float(m.group(3))] if m else current_color
        elif line.startswith("v ") and not line.startswith("vt") and not line.startswith("vn"):
            parts = line[2:].strip().split()
            verts.append([float(p) for p in parts[:3]])
        elif line.startswith("f "):
            idxs = [int(p.split("/")[0]) - 1 - vert_offset for p in line[2:].strip().split()]
            for i in range(1, len(idxs) - 1):
                faces.append([idxs[0], idxs[i], idxs[i + 1]])
                face_colors.append(current_color)
        elif line.startswith("s off"):
            pass

    if not faces:
        print(f"No faces found in {obj_path}")
        return

    verts_a = np.array(verts, dtype=np.float32)
    faces_a = np.array(faces, dtype=np.int32)
    colors_a = np.array(face_colors, dtype=np.float32)

    mesh = trimesh.Trimesh(vertices=verts_a, faces=faces_a)
    mesh.visual = trimesh.visual.ColorVisuals(mesh, vertex_colors=None)
    mesh.visual.face_colors = (colors_a * 255).astype(np.uint8)
    mesh.export(glb_path)
    print(f"{glb_path}: {len(verts)} verts, {len(faces)} faces, colored")


if __name__ == "__main__":
    for name in sys.argv[1:]:
        obj_to_colored_glb(f"outputs/{name}.obj", f"outputs/{name}_colored.glb")
