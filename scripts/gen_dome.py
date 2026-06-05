"""Generate a dome.obj primitive for use in procedural buildings.

Creates a hemisphere with a lantern on top, 0-1 in xy, 0-0.75 in z.
"""

import math

# Parameters
segments = 16
rings = 8
radius = 0.5
cx, cy = 0.5, 0.5
base_z = 0.0
apex_z = 0.5
lantern_height = 0.25
lantern_radius = 0.08

verts = []
faces = []

# Hemisphere vertices
for ring in range(rings + 1):
    theta = (float(ring) / rings) * (math.pi / 2)
    rz = base_z + apex_z * math.sin(theta)
    r = radius * math.cos(theta)
    for seg in range(segments):
        phi = (float(seg) / segments) * 2 * math.pi
        vx = cx + r * math.cos(phi)
        vy = cy + r * math.sin(phi)
        verts.append((vx, vy, rz))

# Hemisphere faces (triangulated quads)
for ring in range(rings):
    for seg in range(segments):
        next_seg = (seg + 1) % segments
        i0 = ring * segments + seg
        i1 = ring * segments + next_seg
        i2 = (ring + 1) * segments + next_seg
        i3 = (ring + 1) * segments + seg
        # Triangulate each quad
        faces.append((i0 + 1, i1 + 1, i2 + 1))
        faces.append((i0 + 1, i2 + 1, i3 + 1))

# Apex vertex
apex_idx = len(verts) + 1
verts.append((cx, cy, base_z + apex_z))

# Cone triangles from top ring to apex
top_ring_start = rings * segments
for seg in range(segments):
    next_seg = (seg + 1) % segments
    i0 = top_ring_start + seg
    i1 = top_ring_start + next_seg
    faces.append((i0 + 1, i1 + 1, apex_idx))

# Lantern: small cupola
lantern_base_z = base_z + apex_z
lantern_apex_z = lantern_base_z + lantern_height
lathe_segs = 8

# Lantern base ring
for seg in range(lathe_segs):
    phi = (float(seg) / lathe_segs) * 2 * math.pi
    vx = cx + lantern_radius * math.cos(phi)
    vy = cy + lantern_radius * math.sin(phi)
    verts.append((vx, vy, lantern_base_z))

lantern_base_start = len(verts) - lathe_segs

# Lantern middle ring (walls)
for seg in range(lathe_segs):
    phi = (float(seg) / lathe_segs) * 2 * math.pi
    vx = cx + lantern_radius * math.cos(phi)
    vy = cy + lantern_radius * math.sin(phi)
    verts.append((vx, vy, lantern_base_z + lantern_height * 0.5))

lantern_mid_start = len(verts) - lathe_segs

# Lantern top ring (smaller)
small_r = lantern_radius * 0.5
for seg in range(lathe_segs):
    phi = (float(seg) / lathe_segs) * 2 * math.pi
    vx = cx + small_r * math.cos(phi)
    vy = cy + small_r * math.sin(phi)
    verts.append((vx, vy, lantern_base_z + lantern_height * 0.8))

lantern_top_start = len(verts) - lathe_segs

# Lantern roof apex
lantern_apex_idx = len(verts) + 1
verts.append((cx, cy, lantern_apex_z))

# Lantern wall faces
for seg in range(lathe_segs):
    next_seg = (seg + 1) % lathe_segs
    b0 = lantern_base_start + seg
    b1 = lantern_base_start + next_seg
    m0 = lantern_mid_start + seg
    m1 = lantern_mid_start + next_seg
    t0 = lantern_top_start + seg
    t1 = lantern_top_start + next_seg
    faces.append((b0 + 1, b1 + 1, m1 + 1))
    faces.append((b0 + 1, m1 + 1, m0 + 1))
    faces.append((m0 + 1, m1 + 1, t1 + 1))
    faces.append((m0 + 1, t1 + 1, t0 + 1))

# Lantern roof triangles
for seg in range(lathe_segs):
    next_seg = (seg + 1) % lathe_segs
    t0 = lantern_top_start + seg
    t1 = lantern_top_start + next_seg
    faces.append((t0 + 1, t1 + 1, lantern_apex_idx))

# Write OBJ
with open("procedural_buildings/primitives/dome.obj", "w") as f:
    f.write("o dome\n")
    for vx, vy, vz in verts:
        f.write(f"v {vx:.6f} {vy:.6f} {vz:.6f}\n")
    f.write("s off\n")
    for f0, f1, f2 in faces:
        f.write(f"f {f0} {f1} {f2}\n")

print(f"Dome generated: {len(verts)} vertices, {len(faces)} faces")
