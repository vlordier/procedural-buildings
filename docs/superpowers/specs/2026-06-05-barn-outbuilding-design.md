# Barn/Shed Outbuilding

## Goal
Add a wooden barn/shed behind the Ukrainian village house on each lot, creating a
farmstead layout.

## Design

### Lot layout change
Each lot with `ukrainianHouse` gets a third section in the `split(y)`:

```
lot(n) : n == 1 -->
  split(y){~1 : pathToHouse | ~(randint(2, 5)) : ukrainianHouse | ~(randint(1, 2)) : barn}
```

The barn sits at the back of the lot, beyond the house.

### Barn parameters
- `woodR/G/B` — weathered brown (0.55, 0.45, 0.35)
- `barnRoofR/G/B` — darker brown roof (0.40, 0.30, 0.20)
- `barnPitch = 0.4` — shallower than house roof
- `barnOverhang = 0.08` — smaller overhang
- `barnHeight = 0.6` — wall portion shorter than house

### Barn structure

```
barn -->
  split(z){
    ~barnHeight : colour(woodR, woodG, woodB){barnWalls}
    | ~barnPitch*(1+2*barnOverhang)/2 : colour(barnRoofR, barnRoofG, barnRoofB){barnRoof}
  }

barnWalls -->
  comp(f){
    front : colour(woodR, woodG, woodB){
      split(x){
        ~1 : I(rect)
        | ~2 : opening(0.1){colour(woodR,woodG,woodB){I(rect)} | nil}
        | ~1 : I(rect)
      }
    }
    left : colour(woodR, woodG, woodB){I(rect)}
    right : colour(woodR, woodG, woodB){I(rect)}
    back : colour(woodR, woodG, woodB){I(rect)}
  }

barnRoof -->
  S(width*(1+2*barnOverhang), depth*(1+2*barnOverhang),
    barnPitch*width*(1+2*barnOverhang)/2)
  T(-width*barnOverhang, -depth*barnOverhang, 0)
  {I(triangle)}
```

### Reuse
The roof logic mirrors `ukrainianHouse` — same `I(triangle)` with S/T for overhang/pitch.

## Testing
- OBJ generates without errors
- Barn visible behind house as a smaller, wood-coloured building with dark roof