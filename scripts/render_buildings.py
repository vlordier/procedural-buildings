"""Step 1: Generate GLB files. Step 2: Render with Blender.
Usage:
    uv run python scripts/render_buildings.py gen      # generates GLBs
    blender -b -P scripts/render_buildings.py -- render # renders GLBs
"""
import os
import sys
import tempfile

OUTPUT_DIR = "/tmp/building_renders"
NUM_BUILDINGS = 5
GLB_DIR = os.path.join(OUTPUT_DIR, "glbs")
RENDER_RES = 640


def generate_glbs():
    os.makedirs(GLB_DIR, exist_ok=True)
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_dir)
    from procedural_buildings.generator import SHOWCASE_GRAMMARS
    from procedural_buildings.Processor import Processor
    import gin

    picks = SHOWCASE_GRAMMARS[:NUM_BUILDINGS]
    import numpy as np
    from procedural_buildings.Scope import Scope
    for i, g in enumerate(picks):
        gin.config.clear_config()
        gin.config.unlock_config()
        gin.parse_config_files_and_bindings(
            [os.path.join(project_dir, "configs/materials_basic.gin")],
            [],
        )
        p = Processor()
        p.grammarDir = os.path.join(project_dir, "grammars") + os.sep
        p.outDir = GLB_DIR + os.sep
        out = os.path.join(GLB_DIR, f"building_{i:04d}.glb")
        s = g["start_scope"]
        scope = Scope.freshScope(np.array(s[:3]), np.array(s[3:]))
        p.grammarToGlb(g["name"], g["start_rule"], scope, out)
        print(f"[{i+1}/{NUM_BUILDINGS}] Generated {out} ({g['name']})")
    print(f"Done. {NUM_BUILDINGS} GLBs in {GLB_DIR}")


def render_glbs():
    import bpy

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for i in range(NUM_BUILDINGS):
        glb_path = os.path.join(GLB_DIR, f"building_{i:04d}.glb")
        if not os.path.exists(glb_path):
            print(f"Skip {glb_path} — not found")
            continue

        # Clear
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)
        for m in list(bpy.data.materials):
            bpy.data.materials.remove(m)
        for m in list(bpy.data.meshes):
            bpy.data.meshes.remove(m)

        # Setup
        scene = bpy.context.scene
        scene.render.engine = "BLENDER_EEVEE"
        scene.render.resolution_x = RENDER_RES
        scene.render.resolution_y = RENDER_RES
        scene.render.film_transparent = True

        # Lights
        for loc, energy, rot in [
            ((5, -3, 6), 800, (1.2, 0, 0.7)),
            ((-4, 2, 3), 300, (0.8, 0, -0.5)),
            ((0, -5, 4), 400, (0.5, 0, 1.6)),
        ]:
            bpy.ops.object.light_add(type="AREA", location=loc)
            l = bpy.context.active_object
            l.data.energy = energy
            l.data.size = 4
            l.rotation_euler = rot

        # Camera
        bpy.ops.object.camera_add(location=(0, -8, 3))
        cam = bpy.context.active_object
        cam.rotation_euler = (0.5, 0, 0)
        scene.camera = cam

        # World
        world = bpy.data.worlds.new(name=f"W{i}")
        world.use_nodes = True
        world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.9, 0.9, 0.95, 1)
        world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.5
        scene.world = world

        # Import
        bpy.ops.import_scene.gltf(filepath=glb_path)

        # Compute bounds from imported meshes
        min_x = min_y = min_z = float("inf")
        max_x = max_y = max_z = float("-inf")
        for obj in bpy.context.scene.objects:
            if obj.type == "MESH":
                for corner in obj.bound_box:
                    wx = obj.matrix_world @ __import__("mathutils").Vector(corner)
                    min_x = min(min_x, wx.x); max_x = max(max_x, wx.x)
                    min_y = min(min_y, wx.y); max_y = max(max_y, wx.y)
                    min_z = min(min_z, wx.z); max_z = max(max_z, wx.z)

        cx = (min_x + max_x) / 2
        cy = (min_y + max_y) / 2
        cz = (min_z + max_z) / 2
        extent = max(max_x - min_x, max_y - min_y, max_z - min_z)
        cam_dist = max(extent * 1.4, 6.0)

        # Camera
        bpy.ops.object.camera_add(location=(cx + cam_dist * 0.7, cy - cam_dist * 0.7, cz + cam_dist * 0.4))
        cam = bpy.context.active_object
        direction = __import__("mathutils").Vector((cx, cy, cz + extent * 0.3)) - cam.location
        rot = direction.to_track_quat("-Z", "Y").to_euler()
        cam.rotation_euler = rot
        scene.camera = cam
        cam.data.lens = 35

        # Render
        png_path = os.path.join(OUTPUT_DIR, f"building_{i:04d}.png")
        scene.render.filepath = png_path
        bpy.ops.render.render(write_still=True)
        print(f"[{i+1}/{NUM_BUILDINGS}] Rendered {png_path}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "gen":
        generate_glbs()
    elif "--" in sys.argv and "render" in sys.argv[sys.argv.index("--") + 1:]:
        render_glbs()
    else:
        print("Usage:")
        print("  uv run python scripts/render_buildings.py gen")
        print("  blender -b -P scripts/render_buildings.py -- render")