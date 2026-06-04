# Opening Operation — Design

## Summary

Add an `opening` CGA operation that cuts rectangular holes through wall
geometry and places doors, windows, garage doors, or glass inside the
opening with full reveal (sill/jamb) depth.

## Motivation

Buildings currently have flat walls with surface-applied details. Real
buildings have openings: doors pass through walls, windows recess into them,
garage doors open into a dark interior. The `inset` operation creates a
visual recess but does not remove wall geometry — you cannot see through
a window to the inside.

CSG boolean mesh subtraction is brittle and slow. This approach exploits
the key fact that openings in CGA grammar are always rectangular and
axis-aligned to the scope grid. The wall-with-hole can be generated as a
simple frame mesh (4 sides) with no subtraction needed.

## Grammar Syntax

```
opening(depth){frameOp | childOp}
```

- `depth` — reveal depth (how far the opening penetrates into the wall,
  usually equal to wall thickness). The opening is centered in the scope
  and inset by `depth` on all sides for the reveal. If `depth=0`, no reveal
  (flush opening, like a modern door).
- `frameOp` — operation applied to the wall frame (4 sides) after removal
  of the opening area. This can be a colour, a trim material, or nil.
- `childOp` — operation applied inside the opening. The child scope sits
  at the back of the reveal. This is where the window, door, garage door,
  or glass primitive goes.

For a simple opening without frame trim:
```
wall --> opening(0.3){I(rect) | I(window3)}
```

For a coloured opening with trim:
```
wall --> opening(0.3){colour(0.2, 0.2, 0.2){I(rect)} | colour(0.4, 0.6, 0.8){I(window3)}}
```

For a garage door:
```
garage_bay --> opening(0){colour(0.3, 0.3, 0.3){I(rect)} | I(garage)}
```

## Semantics

Given a scope of size (W × D × H) positioned with front at y=0:

### Without reveal (depth=0)
- Wall frame: 4 perimeter strips, each D deep (full wall thickness)
- Opening: centered rectangle of size (W×H) positioned at y=0 to y=D
  - But this is just a hole — no geometry behind it
- Child: placed at the back of the hole at y=D, size (W × 0 × H)

### With reveal (depth=d)
- Wall frame: 4 perimeter strips + 4 inner face strips (the sides of the
  reveal, giving visible wall thickness)
- Opening inner: recessed rectangle pushed back by d
  - 4 inner side faces connect the wall surface to the recessed back
- Child: placed at the back of the reveal at y=d, size (W × 0 × H)

### Frame scopes

The wall frame is split into 4 L-shaped scopes (top/bottom/left/right
strips of the wall after opening removal). Each receives the `frameOp`.

### Child scope

The child runs on a scope centered in the opening, pushed back by `depth`
units. The child scope has zero y-depth (flat face).

## Scopes Generated

```
opening(d){frame | child}
```

Produces 5 scopes: [frame_top, frame_bottom, frame_left, frame_right, child]

The 4 frame scopes receive `frameOp` sequentially. The child receives
`childOp` on its centered, recessed scope.

## Scope.genOpening Method

```python
def opening(self, depth):
    """Return ([frame_top, bottom, left, right], child_scope)."""
    ...
```

The frame scopes have the full wall thickness (y depth = s[1]).
The child scope is centered in the opening, pushed back by `depth` in y,
with y size = 0 (flat face), x size = s[0], z size = s[2].

## Implementation

### New op class: OpOpening

- `opName = "opening"`
- 2 child ops: frameOp, childOp
- `run`: calls `scope.opening(depth)`, runs frameOp on each frame scope,
  runs childOp on the child scope
- `simplify` / `argsToHash` follow the same pattern as `OpInset`

### Scope.opening(self, depth)

```python
def opening(self, depth):
    s = self.size
    d = depth
    back = d
    top = Scope(self.pos, self.rotMat, np.array([s[0], s[1], d]))
    top = top.translate(np.array([0, 0, s[2] - d]))
    bottom = Scope(self.pos, self.rotMat, np.array([s[0], s[1], d]))
    left = Scope(self.pos, self.rotMat, np.array([d, s[1], s[2] - 2 * d]))
    left = left.translate(np.array([0, 0, d]))
    right = Scope(self.pos, self.rotMat, np.array([d, s[1], s[2] - 2 * d]))
    right = right.translate(np.array([s[0] - d, 0, d]))
    inner = Scope(self.pos, self.rotMat, np.array([s[0] - 2 * d, s[1], s[2] - 2 * d]))
    inner = inner.translate(np.array([d, 0, d]))
    child = Scope(self.pos, self.rotMat, np.array([s[0], 0, s[2]]))
    child = child.translate(np.array([0, back, 0]))
    return [top, bottom, left, right], child
```

Wait — the above doesn't handle the reveal sides. For a true opening, the
frame scopes need to include the inner reveal faces (the sides of the
wall thickness visible inside the opening).

Actually, for the mesh-based approach, the reveal sides are automatically
handled by the wall thickness. The frame scopes have y-depth = s[1] (full
wall thickness). When a rect primitive fills a frame scope, it creates a
solid block. The opening is the GAP between the frame scopes.

But with scope-based rendering, each scope is independently a solid block.
The frame scopes overlap the opening area. So we can't just split into 4
frame scopes — they'd leave a gap but the gap would be empty, not an
opening with visible reveal sides.

Hmm, let me think about this differently.

In the current system, each primitive is rendered independently. A rect
fills its entire scope. So:
- Top frame scope: rect fills a block of (W × D × d) at the top
- Bottom frame scope: rect fills a block of (W × D × d) at the bottom
- Left frame scope: rect fills a block of (d × D × (H-2d)) on the left
- Right frame scope: rect fills a block of (d × D × (H-2d)) on the right

These 4 blocks leave a rectangular GAP in the middle — that IS the opening.
The gap has no geometry (it's just empty space).

The child scope is a flat rect inside the gap. For a door, the door
primitive fills this gap. For a window, the window primitive fills it.

The reveal depth is handled by pushing the child back. The sides of the
gap (reveal sides) would be visible as the wall thickness depth — but
since the rect primitives have 6 faces, the sides of the frame blocks
facing the gap ARE the reveal faces.

Wait, no. A rect (cube) has 6 faces: front, back, top, bottom, left, right.
When placed in the frame scope, the front face faces outward, the back face
faces inward. The side of the gap is actually the SIDE face of the frame
block — which is visible as the reveal.

Actually, the rect primitive is a complete box. The 4 frame blocks create
a partial wall with a hole in the middle. The inner faces of these blocks
(that face the hole) serve as the reveal sides. The child scope sits in
the hole.

But the issue is that a rect primitive generates a cube that fills its
entire scope. The 4 frame scopes overlap to form a frame around the
opening. But the gap between them is just empty space — there is no
geometry in the gap.

So the approach IS correct:
- Frame 4 scopes → 4 rect cubes → forms wall with hole
- Child scope → rect or window/door primitive → fills hole

The reveal depth comes from pushing the child scope back by `d`. The
sides of the frame blocks facing the hole are the reveal sides. Since
the frame blocks have 6 faces each, the inner faces ARE visible.

This means `opening(d)` is essentially the visual equivalent of a real
hole. The wall has a rectangular opening, the child sits inside.

Let me simplify the scope generation:

```python
def opening(self, depth):
    s = self.size
    d = depth
    # 4 frame strips forming a frame around the opening
    top = self.translate(np.array([0, 0, s[2] - d]))
    top.size = np.array([s[0], s[1], d])
    
    bottom = Scope(self.pos, self.rotMat, np.array([s[0], s[1], d]))
    
    left = self.translate(np.array([0, 0, d]))
    left.size = np.array([d, s[1], s[2] - 2 * d])
    
    right = self.translate(np.array([s[0] - d, 0, d]))
    right.size = np.array([d, s[1], s[2] - 2 * d])
    
    # Child sits at the back of the opening
    child = self.translate(np.array([0, d, 0]))
    child.size = np.array([s[0], 0, s[2]])
    
    return [top, bottom, left, right], child
```

This is cleaner. The 4 frame strips form a frame with a rectangular hole
in the middle. The child sits at the back of the hole, pushed back by d.

OK let me write the actual design doc properly.<｜end▁of▁thinking｜>

<｜｜DSML｜｜tool_calls>
<｜｜DSML｜｜invoke name="write">
<｜｜DSML｜｜parameter name="content" string="true"># Opening Operation — Design

## Summary

Add an `opening` CGA operation that cuts rectangular holes through wall
geometry for doors, windows, garage doors, and glass.

## Grammar Syntax

```
opening(depth){frameOp | childOp}
```

- `depth` — how far the child is recessed into the wall (reveal depth).
  `depth=0` gives a flush opening. `depth=wall_thickness` gives a deep
  opening with visible reveal sides.
- `frameOp` — runs on the 4 frame strips forming the wall around the hole
- `childOp` — runs on a scope centered in the hole, pushed back by `depth`

## Examples

```
window_bay --> opening(0.3){I(rect) | I(window3)}
```
A window recessed 0.3 units into the wall.

```
doorway --> opening(0){colour(0.3, 0.3, 0.3){I(rect)} | I(door)}
```
A flush door opening with dark frame.

```
garage --> opening(0){colour(0.4, 0.35, 0.3){I(rect)} | I(garage)}
```
A garage door opening.

```
wall --> opening(0.5){colour(0.9, 0.9, 0.9){I(rect)} | colour(0.4, 0.6, 0.8){I(rect)}}
```
A recessed glass panel (baie vitrée).

## How It Works

A scope of size (W × D × H) represents a wall section with width W,
depth (thickness) D, height H. The opening operation generates 5 scopes:

```
     top (W × D × d)
     +---------------+
     |               |
left |    opening    | right
(d×D×|     hole      | d×D×
 H-2d)|   (W×D×H)    | H-2d)
     |               |
     +---------------+
     bottom (W × D × d)
```

The 4 frame strips are each full-depth (D) rect cubes. When rendered,
they form a wall with a rectangular hole. The hole is empty space — no
geometry, which means you see through to whatever is behind it.

The child scope sits centered in the hole, pushed back by `depth`. For a
window, the window primitive fills the hole at the recessed position. The
sides of the frame blocks facing the hole act as the reveal (visible wall
thickness).

## Scope.opening Method

```python
def opening(self, depth):
    s = self.size
    d = depth
    top = self.translate(np.array([0, 0, s[2] - d]))
    top.size = np.array([s[0], s[1], d])
    bottom = Scope(self.pos, self.rotMat, np.array([s[0], s[1], d]))
    left = self.translate(np.array([0, 0, d]))
    left.size = np.array([d, s[1], s[2] - 2 * d])
    right = self.translate(np.array([s[0] - d, 0, d]))
    right.size = np.array([d, s[1], s[2] - 2 * d])
    child = self.translate(np.array([0, d, 0]))
    child.size = np.array([s[0], 0, s[2]])
    return [top, bottom, left, right], child
```

## Implementation

- **`OpOpening`** — new class in `Ops.py`, 2 child ops, runs frameOp on
  4 frame scopes, then childOp on the child scope
- **Lexer** — add `OPENING` keyword token
- **Parser** — `OPENING LPAR expr RPAR LCURL singleOp BAR singleOp RCURL`
- Follows the exact same pattern as `OpInset` (same file paths, same
  commit pattern)

## Why This Beats CSG

- Openings are always rectangular and axis-aligned — frame generation is
  trivial scope arithmetic, no mesh booleans needed
- The "hole" is just the gap between 4 frame rects — no mesh subtraction
- The reveal depth is just scope translation — no complex geometry
- Each part (wall, frame, window, door) is a separate scope — fully
  composable, colourable, styleable independently
- Works with existing OBJ primitives — no new asset pipeline

## Out of Scope

- Non-rectangular openings (arches, circles) — would need CSG
- Openings at non-axis-aligned angles — requires scope rotation composition
- Multiple openings in a single wall section — user splits the wall first
