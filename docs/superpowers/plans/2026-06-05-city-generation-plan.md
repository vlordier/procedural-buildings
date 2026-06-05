# City Scene Generation — Plan

**Goal:** Generate full city scenes with procedural street layouts, placed buildings, USD + GLB output.

**Architecture:** 3 waves. Wave 1: street layout generators. Wave 2: building placer + scene data. Wave 3: USD writer.

---

### Wave 1 Task A: Medieval layout generator

**Files:** `procedural_buildings/city/__init__.py`, `procedural_buildings/city/layout.py`

A procedural medieval town generator that outputs block polygons + road segments.

Algorithm:
1. Place center point
2. Generate 4-8 radial main roads with slight curves
3. Place central square (irregular polygon around center)
4. Run recursive subdivision: split blocks along radial + ring directions with random offsets
5. Place cathedral near square (larger block)
6. Generate market street (wider, connecting to one gate)
7. Generate perimeter wall polygon with 2-4 gates
8. Return: list of block polygons, road segments, special feature positions

```python
class MedievalLayout:
    def __init__(self, seed, size="medium"):
        pass
    
    def generate(self):
        # Returns LayoutData with blocks, roads, features
        pass
```

Size presets:
- small: ~100m radius, 10-20 blocks
- medium: ~200m radius, 30-50 blocks
- large: ~400m radius, 80-120 blocks

---

### Wave 1 Task B: Grid layout generator

**Files:** `procedural_buildings/city/layout.py`

A grid city generator.

Algorithm:
1. Create N×M block grid (blocks ~100m × 60m)
2. Designate corridors for wide avenues every 4th street
3. Zone blocks: downtown (center), mid-rise (inner ring), residential (outer)
4. Generate freeway corridor (wide, slightly curved, cuts through one side)
5. Place downtown high-rise cluster (density at center)
6. Return: block polygons, road segments, zones

```python
class GridLayout:
    def __init__(self, seed, size="medium"):
        pass
    
    def generate(self):
        pass
```

Size presets:
- small: 4×4 blocks (~400m × 240m)
- medium: 8×6 blocks (~800m × 360m)
- large: 16×12 blocks (~1600m × 720m)

---

### Wave 2: Building placer

**Files:** `procedural_buildings/city/placer.py`

Takes a LayoutData and assigns buildings to each block.

Rules per zone:
- downtown: modern_district, factory (high complexity)
- residential: cottage, townhouse, medieval_house (low-medium)
- commercial: windmill, barn, bridge (medium-low)
- medieval core: orthodox_church, medieval_house, castle

```python
class BuildingPlacer:
    def __init__(self, layout, seed):
        pass
    
    def place_buildings(self, output_dir):
        # For each block, determine building type + position
        # Generate .glb file
        # Return list of (glb_path, position, rotation) for USD scene
        pass
```

---

### Wave 3: USD scene writer

**Files:** `procedural_buildings/city/writer.py`

Writes `.usda` (text USD) scene file. USD 1.0 format with:
- Ground plane mesh (large subdivided quad)
- Road meshes (flat strips between blocks)
- Building payloads (references to .glb files, transform per building)
- Wall mesh (medieval only)
- Cathedral/monument references

```python
class UsdSceneWriter:
    def __init__(self, output_dir):
        pass
    
    def write(self, layout_data, building_data):
        # Writes city.usda + ground.usd
        pass
```

---

### Wave 3 Task B: CityGenerator facade

**Files:** `procedural_buildings/city/generator.py`

```python
class CityGenerator:
    def __init__(self, style="medieval", seed=None, size="medium"):
        self.style = style
        self.seed = seed
        self.size = size
    
    def generate(self, output_dir):
        layout = self._create_layout()
        layout.generate()
        placer = BuildingPlacer(layout, self.seed)
        buildings = placer.place_buildings(output_dir)
        writer = UsdSceneWriter(output_dir)
        writer.write(layout, buildings)
```

### Testing
```bash
uv run --with sly --with numpy --with sympy --with gin-config python -c "
from procedural_buildings.city import CityGenerator

c = CityGenerator(style='medieval', seed=42, size='small')
c.generate('/tmp/medieval_town')
import os; print(os.listdir('/tmp/medieval_town'))
"
```