# Batch 7: 10 New Grammar Files — Plan

**Goal:** Add 10 new showcase grammars for scene variety. Each one gets
`# @meta`, registers in SHOWCASE_GRAMMARS, and passes tests.

**New grammars:**

| Grammar | Complexity | Materials | Key feature |
|---|---|---|---|
| cottage | low | plaster,roof_tile | Small rural house, simple box + roof |
| barn | low | wood,roof_tile | Large gabled barn |
| lighthouse | medium | stone,glass | Tall tapered tower with lantern room |
| windmill | medium | stone,wood | Tower with roof, optional sails via material |
| greenhouse | low | glass,metal | All-glass walls, sloped glass roof |
| train_station | medium | stone,glass,roof_tile | Long building with canopy roof |
| ruins | low | stone | Broken walls, no roof |
| watchtower | low | stone | Tall narrow tower |
| chapel | medium | stone,roof_tile,glass | Small church with bell tower |
| factory | high | brick,glass,metal | Large industrial with sawtooth roof + chimney |

**New grammars + 12 existing = 22 total in library.**

## Files
- Create: `grammars/cottage`, `grammars/barn`, `grammars/lighthouse`, `grammars/windmill`, `grammars/greenhouse`, `grammars/train_station`, `grammars/ruins`, `grammars/watchtower`, `grammars/chapel`, `grammars/factory`
- Modify: `procedural_buildings/generator.py` (add to SHOWCASE_GRAMMARS)

## Acceptance
- `BuildingGenerator.library()` returns 22 grammars
- All 10 new grammars render without error
- All pass `pytest tests/`