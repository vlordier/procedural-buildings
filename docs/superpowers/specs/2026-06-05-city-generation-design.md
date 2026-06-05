# City Scene Generation — Design

**Goal:** Generate full city scenes with procedural street layouts, placed
buildings, and USD + GLB output.

## Architecture

```
CityGenerator(style, seed, size)
  ├── StreetLayout(style, seed, size)
  │   ├── MedievalLayout
  │   │   - Radial main streets from center
  │   │   - Irregular block subdivision
  │   │   - Central square, cathedral, market street
  │   │   - Perimeter wall with gates
  │   └── GridLayout
  │       - Orthogonal N×M grid
  │       - Wide avenues every 4th street
  │       - Downtown core, mid-rise, suburbs
  │       - Freeway corridor
  ├── BuildingPlacer
  │   - Assigns BuildingGenerator.random to each block
  │   - Respects zoning (downtown=high, suburbs=low)
  │   - Sets position + rotation per building
  └── SceneWriter
      ├── writes city.usda (USD scene referencing .glb files)
      ├── writes individual building .glb files
      └── writes ground plane + road meshes in USD
```

## Output structure
```
output/
├── city.usda
├── ground.usd
└── buildings/
    ├── building_0000.glb
    ├── building_0001.glb
    └── ...
```

## Files
- `procedural_buildings/city/__init__.py`
- `procedural_buildings/city/layout.py` — StreetLayout base + MedievalLayout + GridLayout
- `procedural_buildings/city/placer.py` — BuildingPlacer
- `procedural_buildings/city/writer.py` — UsdSceneWriter
- `procedural_buildings/city/generator.py` — CityGenerator facade

## Acceptance
```python
from procedural_buildings.city import CityGenerator

city = CityGenerator(style="medieval", seed=42)
city.generate("output/medieval_town")
# -> output/medieval_town/city.usda with buildings, walls, streets

city = CityGenerator(style="grid", seed=99)
city.generate("output/la_grid")
# -> output/la_grid/city.usda with grid, freeway, downtown