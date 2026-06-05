# Modern European District Grammar

## Goal
Create `grammars/modern_district` — a city block with modern European buildings:
glass tower, apartment block, and mixed-use building.

## Layout
```
block --> split(y){~1 : road | ~20 : lots | ~1 : road}
lots --> split(x){~(randint(5,8)) : buildingLot | ~0.5 : plaza | ~(randint(5,8)) : buildingLot | ~0.5 : plaza | ~(randint(5,8)) : buildingLot}
buildingLot --> split(y){~0.5 : plaza | ~(randint(3,6)) : modernBuilding}
plaza --> colour(0.6, 0.6, 0.6){I(rect)}
```

## Building types (probabilistic)
```
modernBuilding --> glassTower : 1
modernBuilding --> modernApartment : 1
modernBuilding --> mixedUse : 1
```

### Glass tower
- Tall (15-30 units), glass curtain wall, flat roof
```
glassTower --> S(~1, ~1, randint(15, 30)){colour(glassR, glassG, glassB){comp(f){front : glassFacade | left : colour(glassR,glassG,glassB){I(rect)} | right : colour(glassR,glassG,glassB){I(rect)} | back : colour(glassR,glassG,glassB){I(rect)}}}}
glassFacade --> repeatN(z, 8){split(z){~0.2 : colour(0.2,0.25,0.3){I(rect)} | ~1 : colour(glassR,glassG,glassB){I(rect)}}}
```

### Modern apartment block
- Mid-rise (8-12), white/grey facade, large windows, balconies
```
modernApartment --> split(z){~randint(8,12) : colour(wallR, wallG, wallB){apartmentWalls} | ~0.5 : colour(0.4,0.35,0.3){I(rect)}}
apartmentWalls --> comp(f){front : colour(wallR,wallG,wallB){apartmentFacade} | left : colour(wallR,wallG,wallB){I(rect)} | right : colour(wallR,wallG,wallB){I(rect)} | back : colour(wallR,wallG,wallB){I(rect)}}
apartmentFacade --> repeatN(z, 4){split(z){~0.15 : colour(bandR,bandG,bandB){I(rect)} | ~1 : balconyRow}}
balconyRow --> split(z){~0.1 : colour(0.5,0.5,0.5){I(rect)} | ~1 : colour(wallR,wallG,wallB){split(x){~0.3 : colour(0.5,0.5,0.5){I(rect)} | ~2 : colour(glassR,glassG,glassB){I(rect)} | ~0.3 : colour(0.5,0.5,0.5){I(rect)}}}}
```

### Mixed-use
- Ground floor retail (large windows), upper offices (smaller windows), flat roof
```
mixedUse --> split(z){~3 : retailFloor | ~randint(5,10) : colour(wallR,wallG,wallB){officeWalls} | ~1 : colour(0.3,0.3,0.35){I(rect)}}
retailFloor --> colour(wallR,wallG,wallB){comp(f){front : split(x){~0.5 : I(rect) | ~3 : colour(glassR,glassG,glassB){I(rect)} | ~0.5 : I(rect) | ~3 : colour(glassR,glassG,glassB){I(rect)} | ~0.5 : I(rect)} | left : I(rect) | right : I(rect)}}
officeWalls --> comp(f){front : officeFacade | left : I(rect) | right : I(rect) | back : I(rect)}
officeFacade --> repeatN(z, 3){split(z){~0.1 : colour(0.2,0.25,0.3){I(rect)} | ~1 : colour(glassR,glassG,glassB){split(x){~0.5 : I(rect) | ~2 : colour(glassR,glassG,glassB){I(rect)} | ~0.5 : I(rect)}}}}
```

## Parameters
```
glassR = 0.45
glassG = 0.65
glassB = 0.85
wallR = 0.90
wallG = 0.88
wallB = 0.85
bandR = 0.30
bandG = 0.30
bandB = 0.35
```

## Start rule: `block`

## Testing
```bash
python -m procedural_buildings -i grammars/modern_district -o outputs/modern.obj -s 0,0,0,30,8,25 -R block
```