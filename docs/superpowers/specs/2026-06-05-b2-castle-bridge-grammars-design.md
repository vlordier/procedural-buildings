# B8 — New Grammars: Castle and Bridge

## Goal
Two new showcase grammars: a medieval castle and a stone bridge.

## Castle grammar (`grammars/castle`)
Features: square keep, curtain walls with crenellations, corner towers.
```
keepHeight = 12
towerHeight = 8
wallHeight = 6
stoneR = 0.60
stoneG = 0.55
stoneB = 0.50
roofR = 0.40
roofG = 0.25
roofB = 0.20
plot --> S(~1, ~1, 1){castle}
castle --> colour(stoneR, stoneG, stoneB){comp(f){front : keep | left : wallSegment | right : wallSegment | back : wallSegment} | top : colour(roofR, roofG, roofB){I(rect)}}
keep --> S(~0.4, ~0.4, keepHeight / castleHeight){T(~0.3, ~0.3, 0){split(z){~keepHeight : colour(stoneR, stoneG, stoneB){I(rect)} | ~2 : colour(roofR, roofG, roofB){I(pyramid)}}}}
wallSegment --> ... (crenellated wall with towers at corners)
```
Start rule: `plot`

## Bridge grammar (`grammars/bridge`)
Features: stone arch bridge with pillars and deck.
```
span = 12
pillarW = 2
pillarH = 6
deckThick = 1
stoneR = 0.55
stoneG = 0.50
stoneB = 0.45
plot --> S(~1, ~1, pillarH + deckThick){bridge}
bridge --> ... (pillars + arch + deck)
```
Start rule: `plot`

## Testing
Both grammars should pass `test_grammar_renders` without xfail.
Add to `tests/test_grammars.py` `GRAMMAR_OVERRIDES` if needed.