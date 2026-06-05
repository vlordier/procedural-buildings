# Medieval Half-Timbered House Grammar

## Goal
Create `grammars/medieval_house` — a European medieval half-timbered house
with exposed timber frame, white plaster panels, and steep gabled roof.

## Grammar

```
whiteR = 0.90
whiteG = 0.85
whiteB = 0.80
timberR = 0.30
timberG = 0.20
timberB = 0.15
roofR = 0.65
roofG = 0.35
roofB = 0.20
glassR = 0.60
glassG = 0.70
glassB = 0.80
pitch = 0.65

plot --> S(~1, ~1, 8){medievalHouse}

medievalHouse --> split(z){~5 : walls | ~3 : roof}

walls --> comp(f){
  front : colour(whiteR, whiteG, whiteB){facade}
  left : I(rect)
  right : I(rect)
  back : I(rect)
}

facade --> split(z){
  ~2.5 : split(x){~0.3 : timber | ~2 : panelWin | ~0.3 : timber | ~2 : doorPanel | ~0.3 : timber}
  | ~2.5 : split(x){~0.3 : timber | ~2 : panelWin | ~0.3 : timber | ~2 : panelWin | ~0.3 : timber}
}

panelWin --> colour(whiteR, whiteG, whiteB){
  split(x){~0.15 : timber | ~1.7 : windowUnit | ~0.15 : timber}
}

windowUnit --> split(x){~0.15 : timber | ~1.4 : colour(glassR, glassG, glassB){I(rect)} | ~0.15 : timber}
doorPanel --> colour(whiteR, whiteG, whiteB){split(x){~0.15 : timber | ~1.7 : door | ~0.15 : timber}}
door --> colour(timberR, timberG, timberB){I(rect)}

timber --> colour(timberR, timberG, timberB){I(rect)}

roof --> colour(roofR, roofG, roofB){
  S(width * 1.1, depth * 1.1, pitch * width * 1.1 / 2)
  T(-width * 0.05, -depth * 0.05, 0)
  {I(triangle)}
}
```

## Key details
- Timber grid is built from alternating `I(rect)` panels in cream and dark brown
- The `timber` rule draws a dark brown rect (horizontal or vertical frame member)
- `panelWin` = cream panel with a window set in timber frame
- Roof: standard gabled with clay-tile reddish colour, 10% overhang
- Only the front facade has timber framing — sides are plain cream

## Start rule: `plot`

## Testing
```bash
python -m procedural_buildings -i grammars/medieval_house -o outputs/medieval.obj -s 0,0,0,8,10,8
```