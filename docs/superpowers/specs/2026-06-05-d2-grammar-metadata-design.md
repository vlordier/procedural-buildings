# D2 — Grammar Metadata

## Goal
Every showcase grammar declares its materials, parameters, and complexity
via structured `# @meta` comments. This metadata is parseable by
`BuildingGenerator.get_metadata()` and visible in `grammars/README.md`.

## Format

```grammar
# @meta
# materials: stone, wood, glass
# params: keepHeight=12, towerHeight=8
# complexity: medium
```

Fields:
- `materials`: comma-separated material names used by `material()` calls
- `params`: comma-separated `key=default` pairs (grammar variables a user
  might want to override via gin-config)
- `complexity`: one of `low`, `medium`, `high` — number of primitives
  generated (low < 50, medium < 200, high >= 200)

## Grammars to annotate

All 17 showcase grammars in `grammars/`:

| Grammar | Materials | Key params | Complexity |
|---|---|---|---|
| orthodox_church | plaster, roof_tile, gold | none | medium |
| soviet_block | concrete, glass | numFloors=5, floorHeight=3 | high |
| european_townhouse | plaster, roof_tile | none | medium |
| medieval_house | timber, plaster, roof_tile | none | medium |
| material_building | (gin-configured) | wallPattern=0 | medium |
| warehouse_district | brick, roof_tile, glass | wallHeight=8, roofPitch=0.5 | high |
| modern_district | glass, metal, plaster | none | high |
| site_layout | plaster, roof_tile, brick | none | high |
| facade_city | plaster, roof_tile | none | high |
| castle | stone, roof_tile | keepHeight=12, towerHeight=8 | high |
| bridge | stone | span=12, pillarW=2 | low |
| colored_city | (none — grammatically coloured) | none | high |
| city | (none) | none | high |
| gin_demo | (gin-configured) | panelR=0.75 | medium |
| inset_demo | plaster | none | low |
| neighbor_facade | plaster, roof_tile | none | medium |
| opening_demo | plaster, glass | none | medium |

## Testing
```python
def test_showcase_grammars_have_metadata():
    for grammar in SHOWCASE_GRAMMARS:
        gen = BuildingGenerator(f"grammars/{grammar}")
        meta = gen.get_metadata()
        assert "materials" in meta, f"{grammar} missing materials"
        assert "params" in meta, f"{grammar} missing params"
        assert "complexity" in meta, f"{grammar} missing complexity"
```