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
    from procedural_buildings import BuildingGenerator

    for i in range(NUM_BUILDINGS):
        gen = BuildingGenerator.random(seed=i, materials="configs/materials_basic.gin")
        path = os.path.join(GLB_DIR, f"building_{i:04d}.glb")
        gen.to_glb(path)
        print(f"[{i+1}/{NUM_BUILDINGS}] Generated {path}")
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

        # Center and frame
        bpy.ops.object.select_all(action="DESELECT")
        for obj in bpy.context.scene.objects:
            if obj.type == "MESH":
                obj.select_set(True)
        bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
        bpy.ops.object.location_clear()
        try:
            bpy.ops.view3d.camera_to_view_selected()
        except RuntimeError:
            pass  # workspace may differ

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