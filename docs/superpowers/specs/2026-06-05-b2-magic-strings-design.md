# B1 — Centralize Magic Strings

## Goal
Op names, axis names, and face names are duplicated across `Ops.py`,
`Parser.py`, `Lexer.py`, `Scope.py`. A typo in one but not the other
gives a runtime failure. Centralize as enums.

## Approach
New module `procedural_buildings/_names.py` with `StrEnum` classes.

## File: `procedural_buildings/_names.py`

```python
from enum import StrEnum


class OpName(StrEnum):
    SPLIT = "split"
    REPEAT = "repeat"
    REPEATN = "repeatN"
    COMP = "comp"
    COLOUR = "colour"
    NIL = "nil"
    I = "I"
    S = "S"
    T = "T"
    R = "R"
    SCALE = "scale"
    INSET = "inset"
    OPENING = "opening"
    DO = "do"
    FLIP = "flip"


class Axis(StrEnum):
    X = "x"
    Y = "y"
    Z = "z"


class Face(StrEnum):
    TOP = "top"
    BOTTOM = "bottom"
    FRONT = "front"
    BACK = "back"
    LEFT = "left"
    RIGHT = "right"
```

## Changes to existing files

- `Ops.py` — replace `opName = "split"` with `opName = OpName.SPLIT`
  (16 op classes)
- `Parser.py` — replace `axes = {"x": 0, ...}` with `dict((a.value, i) for i, a in enumerate(Axis))`; replace `colourNames` with `Face` references; replace op-name parser rules with enum values
- `Lexer.py` — replace hardcoded token literals with enum values in
  token definitions where possible
- `Scope.py` — replace face-name if/elif chain with `Face` enum

No behavior change. All tests must pass identically.

## Testing
```bash
pytest tests/ -q
```

Expected: 114 passed, 18 xfailed (unchanged).