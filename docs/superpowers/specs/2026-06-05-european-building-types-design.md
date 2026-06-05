# Soviet Block and European Townhouse Grammars

## Goal
Create two new grammar files for distinct European skyline building types.

---

## 1. `grammars/soviet_block` — Parametric Panel Block

### Key characteristics
- 4-9 story rectangular slab
- Uniform grey/beige concrete panels
- Repetitive window rows
- Flat roof (slight pitch)
- Optional decorative band between floors
- Optional balcony row
- All parameters gin-overridable

### Grammar structure
```
numFloors = 5
floorHeight = 3
panelR = 0.75
panelG = 0.73
panelB = 0.70
bandR = 0.60
bandG = 0.58
bandB = 0.55
glassR = 0.60
glassG = 0.70
glassB = 0.80
windowW = 1.2
windowH = 1.5
plot --> S(~1, ~1, numFloors * floorHeight){sovietBlock}
sovietBlock --> comp(f){front : colour(panelR, panelG, panelB){facade} | left : colour(panelR, panelG, panelB){I(rect)} | right : colour(panelR, panelG, panelB){I(rect)} | back : colour(panelR, panelG, panelB){I(rect)}}
facade --> repeatN(z, numFloors){floor}
floor --> split(z){~0.2 : colour(bandR,bandG,bandB){I(rect)} | ~1 : floorPanel}
floorPanel --> split(z){~1 : colour(panelR,panelG,panelB){I(rect)} | ~windowH : windows}
windows --> repeatN(x, 4){windowUnit}
windowUnit --> split(x){~0.3 : colour(panelR,panelG,panelB){I(rect)} | ~windowW : colour(glassR,glassG,glassB){I(rect)}}
```

### Parameters
| Variable | Default | Gin override example |
|---|---|---|
| numFloors | 5 | 9 |
| panelR | 0.75 | 0.85 |
| panelG | 0.73 | 0.80 |
| panelB | 0.70 | 0.70 |
| windowW | 1.2 | 1.0 |
| windowH | 1.5 | 1.8 |

### Start rule: `plot`

### Example gin configs
`configs/soviet_9story.gin`:
```
grammar_var_overrides.values = {"numFloors": 9, "panelR": 0.85, "panelG": 0.82, "panelB": 0.78, "windowW": 1.0}
```

---

## 2. `grammars/european_townhouse` — Narrow Urban Townhouse

### Key characteristics
- 3-4 stories, narrow (width 6-10)
- Randomised colour per building (cream/ochre/terracotta/grey)
- Steep gabled roof (pitch 0.6-0.7)
- Large street windows with decorative trim
- Ground floor: door + shop window
- Dormer on roof

### Grammar structure
```
wallR = rand/2 + 0.5
wallG = rand/2 + 0.4
wallB = rand/2 + 0.3
roofR = 0.40
roofG = 0.30
roofB = 0.25
townhousePlot --> S(~1, ~1, 12){townhouse}
townhouse --> split(z){~8 : colour(wallR,wallG,wallB){townhouseWalls} | ~4 : townhouseRoof}
townhouseWalls --> comp(f){front : colour(wallR,wallG,wallB){townhouseFacade} | left : colour(wallR,wallG,wallB){I(rect)} | right : colour(wallR,wallG,wallB){I(rect)} | back : colour(wallR,wallG,wallB){I(rect)}}
townhouseFacade --> split(z){~3 : split(x){~1 : I(rect) | ~2 : door | ~2 : windowPair | ~1 : I(rect)} | ~3 : split(x){~1 : I(rect) | ~2 : windowDecor | ~1 : I(rect) | ~2 : windowDecor | ~1 : I(rect)} | ~2 : split(x){~1 : I(rect) | ~2 : windowDecor | ~1 : I(rect) | ~2 : windowDecor | ~1 : I(rect)}}
townhouseRoof --> colour(roofR, roofG, roofB){S(width * 1.1, depth * 1.1, 0.6 * width * 1.1 / 2){T(-width * 0.05, -depth * 0.05, 0){I(triangle)}}}
```

### Testing
```bash
# Soviet block
python -m procedural_buildings -i grammars/soviet_block -o outputs/soviet.obj -s 0,0,0,12,8,15
python -m procedural_buildings -i grammars/soviet_block -o outputs/soviet9.obj -s 0,0,0,12,8,27 -g configs/soviet_9story.gin

# Townhouse
python -m procedural_buildings -i grammars/european_townhouse -o outputs/townhouse.obj -s 0,0,0,8,12,12
```