# B7 — Fix 18 XFailed Grammars

## Goal
Reduce the 18 xfailed grammars to 0. Most fail because they produce
colour-only output (no geometry) or use random expressions without seed.

## Current xfail list (verified from test output)
- `colour_blue` — colour-only output, no geometry
- `ends` — likely empty output
- `fancy_building` — broken
- `present` — empty/colour-only
- `rand_as_rule_priority` — random without seed → non-deterministic
- `rand_in_expr` — random without seed → non-deterministic
- `relative_split` — uses `nil` which may produce colour-only
- `repeat_split_rand` — random + split
- `resize_move_colour` — colour-only
- `rules_as_ops` — old format
- `simple_comp` — may produce mixed output
- `simple_declaration` — variable-only
- `simple_house` — colour-only
- `simple_primitive` — uses primitives that may not exist
- `simple_rand` — random, non-deterministic
- `simple_repeat` — colour-only
- `walled_house` — broken/colour-only
- `params` (op_tests) — parser LALR ambiguity

## Approach
For each xfailed grammar, inspect and decide:
- **Fix** — if a small change makes it produce geometry
- **Archive** — if it's genuinely broken and not worth saving
- **Keep xfail** — if it tests a specific engine edge case that's known
  to produce empty output (e.g., `colour_blue` tests colour with no geom)

## Acceptance
After cleanup, `pytest tests/ -q` shows 0 xfailed.