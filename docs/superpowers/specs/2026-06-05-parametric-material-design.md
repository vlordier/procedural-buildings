# Parametric Material Building

## Goal
A grammar + gin config system where all visual parameters (colours, patterns,
pattern sizes, gradients) are controlled from `.gin` files.

## Approach
Single grammar `grammars/material_building` with conditional rules for each
pattern type. Gin overrides drive all numeric parameters.

## Parameters (gin-overridable)

| Variable | Default | Effect |
|---|---|---|
| wallPattern | 0 | 0=solid, 1=hstripe, 2=vstripe, 3=checker, 4=gradient |
| roofPattern | 0 | Same values |
| wallR/G/B | 0.70, 0.70, 0.70 | Base wall colour |
| patR/G/B | 0.30, 0.30, 0.20 | Pattern/secondary colour |
| roofR/G/B | 0.50, 0.30, 0.20 | Roof colour |
| stripeW | 0.15 | Stripe width (relative to scope) |
| tileS | 0.30 | Checker tile size |

## Grammar

```
-- Parameters (defaults)
wallPattern = 0
roofPattern = 0
wallR = 0.70
wallG = 0.70
wallB = 0.70
patR = 0.30
patG = 0.30
patB = 0.20
roofR = 0.50
roofG = 0.30
roofB = 0.20
stripeW = 0.15
tileS = 0.30
plot --> S(~1, ~1, 12){building}
building --> split(z){~8 : wallSection | ~4 : roofSection}
roofSection --> colour(roofR, roofG, roofB){S(width*1.05, depth*1.05, 2.5){T(-width*0.025, -depth*0.025, 0){I(triangle)}}}
-- Wall pattern selector
wallSection : wallPattern == 0 --> colour(wallR, wallG, wallB){I(rect)}
wallSection : wallPattern == 1 --> repeat(z){~stripeW : colour(patR, patG, patB){I(rect)} | ~stripeW : colour(wallR, wallG, wallB){I(rect)}}
wallSection : wallPattern == 2 --> repeat(x){~stripeW : colour(patR, patG, patB){I(rect)} | ~stripeW : colour(wallR, wallG, wallB){I(rect)}}
wallSection : wallPattern == 3 --> repeat(x){~tileS : split(z){~tileS : colour(wallR, wallG, wallB){I(rect)} | ~tileS : colour(patR, patG, patB){I(rect)}} | ~tileS : split(z){~tileS : colour(patR, patG, patB){I(rect)} | ~tileS : colour(wallR, wallG, wallB){I(rect)}}}
wallSection : wallPattern == 4 --> split(z){~1 : colour(wallR, wallG, wallB){I(rect)} | ~1 : colour(wallR+(patR-wallR)*0.25, wallG+(patG-wallG)*0.25, wallB+(patB-wallB)*0.25){I(rect)} | ~1 : colour(wallR+(patR-wallR)*0.5, wallG+(patG-wallG)*0.5, wallB+(patB-wallB)*0.5){I(rect)} | ~1 : colour(wallR+(patR-wallR)*0.75, wallG+(patG-wallG)*0.75, wallB+(patB-wallB)*0.75){I(rect)} | ~1 : colour(patR, patG, patB){I(rect)}}
```

## Gin configs

`configs/brick.gin` — solid brick wall, dark roof:
```
grammar_var_overrides.values = {"wallPattern": 0, "wallR": 0.70, "wallG": 0.30, "wallB": 0.20, "roofR": 0.40, "roofG": 0.25, "roofB": 0.20}
```

`configs/nordic.gin` — white wall, blue horizontal stripe:
```
grammar_var_overrides.values = {"wallPattern": 1, "wallR": 0.95, "wallG": 0.92, "wallB": 0.88, "patR": 0.20, "patG": 0.40, "patB": 0.55, "stripeW": 0.1}
```

`configs/checker.gin` — cream + brown checkerboard:
```
grammar_var_overrides.values = {"wallPattern": 3, "wallR": 0.95, "wallG": 0.90, "wallB": 0.85, "patR": 0.60, "patG": 0.50, "patB": 0.35, "tileS": 0.3}
```

`configs/gradient.gin` — white-to-blue gradient:
```
grammar_var_overrides.values = {"wallPattern": 4, "wallR": 0.95, "wallG": 0.95, "wallB": 0.95, "patR": 0.20, "patG": 0.40, "patB": 0.60}
```

## Testing
```bash
python -m procedural_buildings -i grammars/material_building -o outputs/material.obj -s 0,0,0,8,8,12
python -m procedural_buildings -i grammars/material_building -o outputs/checker.obj -s 0,0,0,8,8,12 -g configs/checker.gin
```