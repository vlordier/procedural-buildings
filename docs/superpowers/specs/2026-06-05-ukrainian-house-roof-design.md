# Ukrainian Village House with Parametric Roofs

## Goal
Replace the placeholder houses in `grammars/site_layout` with Ukrainian village-style
houses (khata) using grammar-only parametric roof primitives.

## Design Decisions

### Grammar-only approach
Roofs are composed from the existing `I(triangle)` primitive using `S()` and `T()` to
express pitch and overhang as grammar-level parameters. No engine changes needed.

### Roof geometry
`I(triangle)` is a triangular prism with bounding box (0,0,0)-(1,1,1), mapped to unit
cube then to the scope. In a scope of (span, depth, height):
- Ridge runs along the y-axis (depth) at x=0, z=+height/2
- Base spans x from -span/2 to +span/2

Pitch = rise / half-span, so: **roofHeight = pitch × span / 2**

Overhang extends the roof scope past the wall footprint:
```
roof -->
  S(width * (1 + 2*overhang), depth * (1 + 2*overhang), pitch * width * (1 + 2*overhang) / 2)
  T(-width * overhang, -depth * overhang, 0)
  {I(triangle)}
```

### House structure
```
split(z){~1 : walls | ~roofHeight : colour(thatch){roof}}
```

### Wall facade
`comp(f)` selects front/back/left/right faces. The front wall uses `split(x)` and
`split(z)` to arrange windows (with blue shutters) and a blue door. A thin
decorative band (`decorHeight`) is placed at the top of the wall section, spanning
the overhang width via `S(~(1+2*overhang), ...)`.

### Parameters exposed as grammar variables
- `pitch` — roof steepness (rise/run ratio, e.g. 0.6)
- `overhang` — fraction of wall width extending past each side
- `thatch(R,G,B)` — warm golden-brown
- `wall(R,G,B)` — cream/white plaster
- `shutter(R,G,B)` — blue
- `door(R,G,B)` — blue

### Site integration
`grammars/site_layout` updated: `lot(0)` keeps the existing tower (modern contrast),
`lot(1)` and `lot(2)` get Ukrainian houses. A `pathToHouse` rule adds a front path
with a white picket fence section.

## Concrete Grammar

```grammar
-- Parameters
pitch = 0.6
overhang = 0.12

-- Colours
thatchR = 0.55; thatchG = 0.40; thatchB = 0.25
wallR = 0.95; wallG = 0.92; wallB = 0.88
shutterR = 0.20; shutterG = 0.35; shutterB = 0.55
doorR = 0.20; doorG = 0.35; doorB = 0.55
bandR = 0.85; bandG = 0.70; bandB = 0.60
decorHeight = 0.05

-- Site layout
road --> colour(0.2, 0.2, 0.2){I(rect)}
path --> colour(0.3, 0.3, 0.3){I(rect)}
block --> split(y){~1 : road | ~20 : lots | ~1 : road}

lots --> split(x){
  ~(randint(4, 7)) : lot(0)
  | ~1 : path
  | ~(randint(5, 8)) : lot(1)
  | ~1 : path
  | ~(randint(4, 7)) : lot(2)
}

lot(n) : n == 0 -->
  colour(0.6, 0.5, 0.4){
    split(y){~1 : colour(0.3, 0.3, 0.3){I(rect)} | ~(randint(3, 6)) : tower(n)}
  }

lot(n) : n == 1 -->
  split(y){~1 : pathToHouse | ~(randint(2, 5)) : ukrHouse}

lot(n) : n == 2 -->
  split(y){~1 : pathToHouse | ~(randint(2, 5)) : ukrHouse}

pathToHouse -->
  split(x){
    ~1 : colour(0.3, 0.3, 0.3){I(rect)}
    | ~0.08 : colour(0.85, 0.85, 0.85){
        split(z){~0.4 : nil | ~0.6 : I(rect)}
      }
    | ~1 : colour(0.3, 0.3, 0.3){I(rect)}
  }

ukrHouse -->
  split(z){
    ~1 : walls
    | ~pitch * (1 + 2*overhang)/2 :
        colour(thatchR, thatchG, thatchB){roof}
  }

walls -->
  split(z){
    ~decorHeight : colour(bandR, bandG, bandB){
      S(~(1 + 2*overhang), ~(1 + 2*overhang), ~1){I(rect)}
    }
    | ~1 : comp(f){
        front : colour(wallR, wallG, wallB){frontWall}
        left  : colour(wallR, wallG, wallB){I(rect)}
        right : colour(wallR, wallG, wallB){I(rect)}
        back  : colour(wallR, wallG, wallB){I(rect)}
      }
  }

frontWall : width > 7 -->
  split(z){
    ~2.5 : split(x){
      ~1 : I(rect) | ~1.5 : door | ~1.5 : windowPair | ~1 : I(rect)
    }
    | ~1 : split(x){
      ~1 : I(rect) | ~1.5 : windowPair | ~1 : I(rect)
      | ~1.5 : windowPair | ~1 : I(rect)
    }
  }

frontWall -->
  split(z){
    ~2.5 : split(x){~1 : I(rect) | ~1.5 : door | ~1 : I(rect)}
    | ~1 : split(x){~1 : I(rect) | ~1.5 : windowPair | ~1 : I(rect)}
  }

windowPair --> split(x){~0.3 : shutter | ~1.5 : windowUnit | ~0.3 : shutter}
windowUnit --> opening(0.15){colour(0.9, 0.92, 0.95){I(rect)} | I(window3)}
shutter --> colour(shutterR, shutterG, shutterB){I(rect)}
door --> opening(0.1){colour(doorR, doorG, doorB){I(rect)} | I(door)}

roof -->
  S(width * (1 + 2*overhang), depth * (1 + 2*overhang),
    pitch * width * (1 + 2*overhang) / 2)
  T(-width * overhang, -depth * overhang, 0)
  {I(triangle)}

-- Tower kept for variety
tower(n) : n == 0 -->
  split(x){~1 : I(column) | ~4 : opening(0.3){I(rect) | I(window3)} | ~1 : I(column)}
tower(n) -->
  split(x){~1 : I(column) | ~4 : opening(0.3){I(rect) | I(window3)}
    | ~1 : I(column) | ~4 : opening(0.3){I(rect) | I(window3)} | ~1 : I(column)}
```

## Required Engine Change

**One line** in `procedural_buildings/Ops.py:385`:

```python
# Before:
child.run(context, scope, env)
# After:
child.run(context, scope, scope_env)
```

This makes `width` / `depth` / `height` (from the current scope) available to all
child operations, not just condition evaluation. It is a natural expectation that
scope dimensions are available everywhere in the grammar.

Without this change, operations like `S(width * (1 + 2*overhang), ...)` and
`T(-width * overhang, ...)` would fail with unresolved symbol errors.

## Key Implementation Details

1. The `roof` rule uses `width` and `depth` from the current scope env (passed via
   `scope_env` in `OpChooseRuleWithPriority.run()`). This works because the roof is
   a child of `split(z)` on the house scope, which has the correct wall footprint size.

2. The `T(-overhang * width, ...)` re-centers the overhanging roof. Without it, the
   `S()` would grow from the origin corner, shifting the roof off-center.

3. The decorative band is a thin horizontal rect at the top of the wall section,
   scaled to span the overhang width via `S(~(1+2*overhang), ...)`.

4. `frontWall` has two rules: one for `width > 7` (wider houses get 4 windows, 2 per
   floor) and the fallback for narrower houses (2 windows, 1 per floor).

## Testing
- Run with: `python -m procedural_buildings -i grammars/site_layout -o outputs/site.obj -s 0,0,0,40,5,20 -R block`
- Convert to GLB: `python scripts/obj_to_glb_colored.py site`
- Verify: houses have white walls, steep thatch roofs with visible overhang, blue
  shutters, a blue door, and a decorative band at the top of the wall
