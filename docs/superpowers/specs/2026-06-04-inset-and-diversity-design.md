# Inset Operation & Primitive Diversity

## Summary

Add an `inset` operation to the CGA shape grammar and expand the primitive library
to increase architectural diversity of generated buildings.

## Motivation

Buildings currently look boxy because:
- Everything is flat splits — no depth or recessing
- Primitive shapes are limited to basic geometry (rect, triangle, pyramid)
- No operation creates frames, panels, or inset details

Adding `inset` provides an immediate visual improvement with minimal engine
changes. Combined with new primitives, it unlocks varied facades without
requiring grammar-language redesign.

## Inset Operation

### Syntax

```
inset(offset){frameOp | innerOp}
```

- `offset` — distance to inset (numeric expression, supports `rand()`, arithmetic)
- `frameOp` — operation applied to the 4 perimeter strips
- `innerOp` — operation applied to the central shrunken scope

### Semantics

Given a scope of width W and height H, insetting by `d` produces 5 scopes:

```
+-----------------------+
|    top (W x d)        |
+-------+-------+-------+
| left  | inner | right |
| (d x  |(W-2d) |(d x   |
| H-2d) |x H-2d)| H-2d) |
+-------+-------+-------+
|   bottom (W x d)      |
+-----------------------+
```

Each of the 4 frame scopes receives the `frameOp` — applied sequentially (top,
bottom, left, right). The inner scope receives the `innerOp`.

### Examples

Simple recessed panel:
```
panel --> inset(0.5){I(rect) | I(rect)}
```

Window bay with frame and glass:
```
bay --> inset(0.3){colour(grey) I(rect) | colour(blue) I(window)}
```

Deeply nested details:
```
detail --> inset(0.2){I(rect) | inset(0.1){I(rect) | I(rect)}}
```

### Implementation

- **`Scope.inset(amount)`** — returns tuple of 5 scopes
- **`OpInset`** — new class in `Ops.py`, 2 child ops, calls `scope.inset()` then
  applies frameOp 4 times then innerOp once
- **Lexer** — add `INSET` keyword token
- **Parser** — add `INSET LPAR expr RPAR LCURL singleOp BAR singleOp RCURL`
- **`OpInset.simplify`** — deduplication via hash (same args + same children)
- **`OpInset._toGrammarText`** — serialize back to grammar format

## New Primitives

Add 5 OBJ files to `procedural_buildings/primitives/`:

| Primitive | Description | Geometry |
|-----------|-------------|----------|
| `arch` | Classic arched opening | 1m wide, 2m tall, arch top |
| `column` | Fluted column | 0.5m diameter, 3m tall |
| `balcony` | Balcony with railing | 2m wide, 1m deep |
| `dormer` | Roof dormer window | 1.5m wide, 1.5m tall |
| `pediment` | Triangular pediment | 2m wide base, 1m peak |

Each OBJ follows the existing convention: centered at origin, unit-sized for
scoping, with vertex indices and face data.

## Leveraging Existing Features

The following already work but are underused — they'll be demonstrated in
richer example grammars:

- `rand(low, high)` / `randint(low, high)` — random split sizes, counts
- Probabilistic rule selection — `: 0.7` priorities
- `repeatN(axis, n)` — with `randint` for varied floors
- `comp(f)` — per-face decomposition (top, bottom, front, etc.)

## Example Grammar

A 5-rule grammar demonstrating the full pipeline:

```
N = randint(3, 6)
plot --> split(y){~1 : base | ~(N*3) : floors(0) | ~1 : roof}
floors(i) :
  i < N : split(y){~3 : floor | ~0.5 : band | ~(N*3) : floors(i+1)} |
  i >= N : split(y){~3 : floor}
floor --> colour(tan) split(x){~1 : I(column) | ~4 : bay | ~1 : I(column)}
bay --> inset(0.3){colour(dark) I(rect) | colour(light) I(window)}
base --> colour(grey) I(rect)
```

Run with `-n 5` to generate 5 different buildings with 3-6 floors each, varied
window arrangements, and recessed bay windows with visible frames.

## Out of Scope

- Full constraint system (scope queries in conditions) — separate project
- MTL/colour export — colours are comments in OBJ for now
- `extrude` operation — would require mesh manipulation beyond current scope
- Face-specific inset (e.g., inset only top or left) — future extension
