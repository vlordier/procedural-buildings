# C1 — UV Coordinates on All Primitives

## Goal
Every `.obj` file in `procedural_buildings/primitives/` must have valid
UV coordinates (`vt` entries) on their vertices, so that the GLB export
can write UV data into the mesh buffers.

## Current state
- `rect.obj` — has 6 UVs for 8 verts (per-face planar mapping), partial
- `triangle.obj` — no UVs, has normals
- `pyramid.obj` — no UVs
- Most others — mixed state

## Approach
For each primitive, add `vt` lines and update faces to reference
`v/vt/vn` triplets. The UV mapping strategy:

- **Box-like primitives** (rect, column, arch): planar UV per face,
  each face maps to [0,1]² in UV space (standard cubemap layout)
- **Flat primitives** (triangle, right_angle_triangle): planar XY,
  map bounding box to [0,1]²
- **Pyramid**: planar UV per triangle face
- **Sphere-like** (dome): spherical projection (u = atan2(z,x), v = asin(y))
- **Other** (hip, trough, pediment, dormer): best-fit planar projection

## Primitives to update (21 files)
```
arch, balcony, cabinEntrance, cabinRoof, cabinWindow, column, corner,
dome, door, dormer, garage, hip, pediment, pyramid, rect, rect_old,
right_angle_triangle, roofCorner, triangle, trough, window2, window3
```

## Testing
Ensure all existing tests still pass (UVs don't change geometry):
```bash
pytest tests/ -q
```