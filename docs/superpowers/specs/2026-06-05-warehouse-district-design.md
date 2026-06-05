# Warehouse District with Sawtooth and Gabled Roofs

## Goal
Create `grammars/warehouse_district` — an industrial zone with large warehouses
that randomly pick between gabled and sawtooth roof styles.

## Design

### Layout
A street block subdivided into 3 warehouse lots, each with a truck bay in front:

```
block --> split(y){~1 : road | ~30 : lots | ~1 : road}
lots --> split(x){
  ~(randint(6, 10)) : warehouseLot
  | ~0.5 : path
  | ~(randint(6, 10)) : warehouseLot
  | ~0.5 : path
  | ~(randint(6, 10)) : warehouseLot
}
warehouseLot --> split(y){~1 : truckBay | ~(randint(4, 8)) : warehouse}
truckBay --> colour(0.2, 0.2, 0.2){I(rect)}
```

### Warehouse structure
```
warehouse -->
  split(z){
    ~wallHeight : colour(brickR, brickG, brickB){warehouseWalls}
    | ~roofHeight : warehouseRoof
  }
```

### Walls
Brick-coloured (`0.70, 0.30, 0.20`) with 2 loading bay openings on the front.

### Roof variants (probabilistic, equal weight)
1. **Gabled:** Standard gabled roof — `I(triangle)` with S/T for pitch/overhang.
2. **Sawtooth:** 4 repeated teeth. Each tooth: thin glass vertical rect +
   `I(right_angle_triangle)` sloped panel in dark roof colour.

```
warehouseRoof --> gabledWarehouseRoof : 1
warehouseRoof --> sawtoothRoof : 1

gabledWarehouseRoof -->
  colour(roofR, roofG, roofB){
    S(width*(1+2*roofOverhang), depth*(1+2*roofOverhang), roofPitch*width*(1+2*roofOverhang)/2)
    T(-width*roofOverhang, -depth*roofOverhang, 0)
    {I(triangle)}
  }

sawtoothRoof -->
  colour(roofR, roofG, roofB){
    repeatN(x, 4){sawtoothTooth}
  }

sawtoothTooth -->
  split(x){
    ~0.08 : colour(glassR, glassG, glassB){I(rect)}
    | ~1 : I(right_angle_triangle)
  }
```

### Parameters
```
brickR = 0.70
brickG = 0.30
brickB = 0.20
roofR = 0.30
roofG = 0.25
roofB = 0.20
glassR = 0.60
glassG = 0.70
glassB = 0.80
wallHeight = 8
roofPitch = 0.5
roofOverhang = 0.10
```

## Testing
```bash
python -m procedural_buildings -i grammars/warehouse_district -o outputs/wardist.obj -s 0,0,0,40,10,20
python scripts/obj_to_glb_colored.py wardist
```
Expected: 3 warehouses with mix of gabled and sawtooth roofs, brick walls, glass sawtooth faces.