"""Open a city USD scene in Blender with Eevee rendering.
Usage: blender -P scripts/view_city_blender.py -- /tmp/city_show/city.usda
"""
import json
import os
import re
import sys
import struct

import bpy


def read_usda(path):
    """Parse our simple USD format for building data."""
    with open(path) as f:
        lines = f.readlines()
    buildings = []
    base_dir = os.path.dirname(os.path.abspath(path))
    i = 0
    while i < len(lines):
        line = lines[i]
        if 'def Xform "building_' in line:
            # Collect the block until the matching }
            block = ""
            depth = 0
            started = False
            while i < len(lines):
                c = lines[i]
                block += c
                if "{" in c:
                    depth += 1
                    started = True
                if "}" in c:
                    depth -= 1
                if started and depth == 0:
                    break
                i += 1
            # Extract payload and transform
            pm = re.search(r"@([^@]+\.glb)@", block)
            tm = re.search(r"xformOp:translate = \(([^)]+)\)", block)
            rm = re.search(r"xformOp:rotateXYZ = \(([^)]+)\)", block)
            if pm and tm:
                glb_rel = pm.group(1)
                glb_path = os.path.join(base_dir, glb_rel)
                tx, ty, tz = (float(x) for x in tm.group(1).split(","))
                ry = float(rm.group(1).split(",")[1]) if rm else 0
                if os.path.exists(glb_path):
                    buildings.append({"glb": glb_path, "pos": (tx, ty, tz), "rot": ry})
        i += 1
    return buildings


def load_glb_vertices(path):
    """Extract vertex positions from a GLB to compute bounding box."""
    with open(path, "rb") as f:
        data = f.read()
    pos = 12
    json_str = None
    while pos < len(data):
        chunk_len = struct.unpack_from("<I", data, pos)[0]
        chunk_type = struct.unpack_from("<I", data, pos + 4)[0]
        chunk_start = pos + 8
        if chunk_type == 0x4E4F534A:
            json_str = data[chunk_start:chunk_start + chunk_len].decode("utf-8")
            break
        pos += 8 + chunk_len
    if not json_str:
        return 0
    doc = json.loads(json_str)
    accessors = doc.get("accessors", [])
    bvs = doc.get("bufferViews", [])
    if not accessors:
        return 0
    pos_acc = accessors[0]
    bv = bvs[pos_acc.get("bufferView", 0)]
    count = pos_acc.get("count", 0)
    # Read min/max from accessor
    mn = pos_acc.get("min", [0, 0, 0])
    mx = pos_acc.get("max", [0, 0, 0])
    return (count, mn, mx)


def setup_scene(buildings):
    """Set up Blender scene with city buildings."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    # Set up Eevee
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

    # Add sun light
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 100))
    sun = bpy.context.active_object
    sun.data.energy = 5
    sun.rotation_euler = (0.8, 0, 0.5)

    # Add camera
    bpy.ops.object.camera_add(location=(150, -100, 80))
    cam = bpy.context.active_object
    cam.rotation_euler = (1.1, 0, 0.8)
    scene.camera = cam

    # Import each building GLB
    for i, b in enumerate(buildings):
        try:
            bpy.ops.import_scene.gltf(filepath=b["glb"])
            obj = bpy.context.selected_objects[0]
            obj.location = b["pos"]
            obj.rotation_euler = (0, 0, b["rot"])
            obj.name = f"building_{i:04d}"
        except Exception as e:
            print(f"Failed to import {b['glb']}: {e}")

    # Add a ground plane
    bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, -0.5))
    ground = bpy.context.active_object
    ground.name = "Ground"

    # Add a simple material to ground
    mat = bpy.data.materials.new(name="GroundMat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.3, 0.35, 0.25, 1)
    bsdf.inputs["Roughness"].default_value = 0.9
    ground.data.materials.append(mat)

    # Frame all objects
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.view3d.camera_to_view_selected()

    # Set viewport to solid shading with Eevee
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            area.spaces[0].shading.type = "MATERIAL"
            area.spaces[0].shading.use_scene_lights = True
            area.spaces[0].shading.use_scene_world = True

    print(f"Imported {len(buildings)} buildings")


if __name__ == "__main__":
    argv = sys.argv
    usda_path = argv[argv.index("--") + 1] if "--" in argv else None
    if not usda_path:
        print("Usage: blender -P view_city_blender.py -- /path/to/city.usda")
        sys.exit(1)

    print(f"Loading city scene from {usda_path}")
    buildings = read_usda(usda_path)
    print(f"Found {len(buildings)} buildings")
    setup_scene(buildings)