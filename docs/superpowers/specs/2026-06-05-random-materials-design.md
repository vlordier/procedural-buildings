# Batch 6: Random Material Palettes — Spec

**Goal:** When `BuildingGenerator.random()` is called without a
fixed materials file, assign random material colours from curated
palettes so batch outputs are visually diverse.

## Random material assignment

When `materials=None` in `BuildingGenerator.random()`, instead of
loading no materials (which leaves things grey), generate a random
set of material presets based on the building's grammar metadata.

```python
gen = BuildingGenerator.random(seed=42)
# Automatically gets random colours for its declared materials
# e.g., stone=[0.6,0.55,0.5] might become sandstone=[0.8,0.6,0.3]
```

## Material palettes

A set of curated colour palettes in `materials.py`:

```python
MATERIAL_PALETTES = {
    "stone": [
        [0.60, 0.55, 0.50],  # grey
        [0.70, 0.60, 0.50],  # warm grey
        [0.55, 0.50, 0.45],  # dark grey
        [0.80, 0.60, 0.30],  # sandstone
        [0.75, 0.70, 0.65],  # light grey
    ],
    "brick": [
        [0.70, 0.30, 0.20],  # red
        [0.60, 0.25, 0.15],  # dark red
        [0.75, 0.40, 0.25],  # terracotta
        [0.55, 0.35, 0.20],  # brown
    ],
    "roof_tile": [
        [0.40, 0.25, 0.20],  # dark brown
        [0.30, 0.15, 0.10],  # very dark
        [0.50, 0.30, 0.20],  # mid brown
        [0.35, 0.25, 0.20],  # warm brown
    ],
    "plaster": [
        [0.85, 0.82, 0.78],  # white
        [0.90, 0.85, 0.75],  # cream
        [0.80, 0.75, 0.70],  # light beige
        [0.92, 0.88, 0.82],  # off white
        [0.75, 0.72, 0.68],  # warm beige
    ],
    "wood": [
        [0.55, 0.35, 0.15],  # medium
        [0.45, 0.28, 0.12],  # dark
        [0.60, 0.40, 0.20],  # light
        [0.50, 0.30, 0.10],  # walnut
    ],
    "glass": [
        [0.60, 0.70, 0.80],  # blue
        [0.50, 0.60, 0.70],  # dark blue
        [0.70, 0.80, 0.90],  # light blue
        [0.80, 0.80, 0.85],  # grey
    ],
    "concrete": [
        [0.75, 0.73, 0.70],  # standard
        [0.70, 0.65, 0.60],  # warm
        [0.65, 0.68, 0.72],  # blue-grey
        [0.80, 0.78, 0.75],  # light
    ],
    "metal": [
        [0.50, 0.50, 0.50],  # grey
        [0.60, 0.55, 0.50],  # bronze
        [0.70, 0.70, 0.72],  # silver
        [0.40, 0.42, 0.45],  # dark
    ],
    "gold": [
        [0.90, 0.75, 0.30],  # gold
        [0.85, 0.70, 0.25],  # dark gold
    ],
    "timber": [
        [0.50, 0.30, 0.15],  # dark
        [0.60, 0.40, 0.20],  # medium
        [0.45, 0.25, 0.10],  # very dark
    ],
}
```

## Changes

- `materials.py` — add `MATERIAL_PALETTES`, add `random_material_presets(seed)`
- `generator.py` — in `random()`, when `materials=None`, generate random presets

## Files
- Modify: `procedural_buildings/materials.py`, `procedural_buildings/generator.py`

## Acceptance
```python
gen = BuildingGenerator.random(seed=42)
gen.to_glb("/tmp/random_mat.glb")
# Has coloured materials, not grey
```