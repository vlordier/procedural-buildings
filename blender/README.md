# Blender Integration

Files salvaged from `legacy/` directory. These provide:
- **`blender_ops.py`** - Blender bmesh operations (mesh bisect/split)
- **`context_blender.py`** - Blender context for running CGA grammars on live Blender meshes
- **`psb2.py`** - Blender addon with UI panel and file picker

## Status

These files are a starting point for Blender integration but are not currently wired into the package. The `psb2.py` addon needs to be loaded as a Blender addon, and the grammar-running pipeline needs to be connected to the Blender UI.

## Usage

In Blender: Edit > Preferences > Add-ons > Install, then select `psb2.py`.