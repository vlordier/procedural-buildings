# B9 — GLB Viewer Improvements

## Goal
Improve the OBJ-to-GLB conversion and the Pyglet viewer for better
visualization of coloured grammars.

## Viewer: `procedural_buildings/view.py`
- Fix lighting: add a directional light from upper-right
- Enable smooth shading (flat per-face for OBJ-style)
- Add orbit controls via mouse drag (improve on current rotation)
- Add wireframe toggle (`w` key)

## GLB export: `scripts/obj_to_glb.py`
- Now that colour is engine-native (cluster 2), ensure GLB export reads
  colour from OBJ comments (`# colour(r,g,b)`) and applies as vertex
  colours or material colours
- Support multi-material output (one material per colour)

## Acceptance
- `python -m procedural_buildings.view outputs/example.obj` shows the
  building with correct colours and lighting
- `python scripts/obj_to_glb.py example` produces a `.glb` with colour
  materials