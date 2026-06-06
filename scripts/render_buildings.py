"""Render 10 individual building assets with Eevee.
Usage: blender -P scripts/render_buildings.py
"""
import os
import sys
import tempfile

import bpy

OUTPUT_DIR = "/tmp/building_renders"
NUM_BUILDINGS = 10


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat)
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)


def setup_scene():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.film_transparent = True
    scene.render.dither_intensity = 0

    # Eevee settings
    scene.eevee.taa_render_samples = 64
    scene.eevee.bloom_intensity = 0

    # HDRI lighting via a simple setup
    # Key light
    bpy.ops.object.light_add(type="AREA", location=(5, -3, 6))
    key = bpy.context.active_object
    key.data.energy = 800
    key.data.size = 4
    key.rotation_euler = (1.2, 0, 0.7)

    # Fill light
    bpy.ops.object.light_add(type="AREA", location=(-4, 2, 3))
    fill = bpy.context.active_object
    fill.data.energy = 300
    fill.data.size = 3
    fill.rotation_euler = (0.8, 0, -0.5)

    # Rim light
    bpy.ops.object.light_add(type="AREA", location=(0, -5, 4))
    rim = bpy.context.active_object
    rim.data.energy = 400
    rim.data.size = 3
    rim.rotation_euler = (0.5, 0, 1.6)

    # Camera
    bpy.ops.object.camera_add(location=(0, -8, 3))
    cam = bpy.context.active_object
    cam.rotation_euler = (0.5, 0, 0)
    scene.camera = cam

    # World background (solid light grey for soft shadows)
    world = bpy.data.worlds.new("RenderWorld")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.9, 0.9, 0.95, 1)
    bg.inputs["Strength"].default_value = 0.5
    scene.world = world


def import_and_render(glb_path, output_path, idx):
    clear_scene()
    setup_scene()

    # Import GLB
    bpy.ops.import_scene.gltf(filepath=glb_path)

    # Center object and compute bounds
    bpy.ops.object.select_all(action="DESELECT")
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.select_set(True)
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")

    # Move to origin
    bpy.ops.object.location_clear()

    # Frame the object with camera
    bpy.ops.view3d.camera_to_view_selected()

    # Set output and render
    scene = bpy.context.scene
    scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)

    print(f"[{idx+1}/{NUM_BUILDINGS}] Rendered to {output_path}")


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Add project to path
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)

    from procedural_buildings import BuildingGenerator

    for i in range(NUM_BUILDINGS):
        gen = BuildingGenerator.random(seed=i, materials="configs/materials_basic.gin")
        glb_path = os.path.join(tempfile.gettempdir(), f"render_{i:04d}.glb")
        gen.to_glb(glb_path)
        png_path = os.path.join(OUTPUT_DIR, f"building_{i:04d}.png")
        import_and_render(glb_path, png_path, i)
        os.remove(glb_path)

    print(f"\nDone! {NUM_BUILDINGS} renders in {OUTPUT_DIR}")
    for f in sorted(os.listdir(OUTPUT_DIR)):
        path = os.path.join(OUTPUT_DIR, f)
        size = os.path.getsize(path)
        print(f"  {f}: {size / 1024:.0f} KB")