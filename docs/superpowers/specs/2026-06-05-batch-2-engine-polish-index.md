# Batch 2: Engine Polish & Content — Index

**Goal:** Polish the engine with 9 low-to-medium effort improvements:
magic string centralization, Lexer fix, 3 new ops/features, colour lifting,
grammar fixes, new content, and viewer improvements.

## Items

| # | Item | Group | Effort | Depends on |
|---|---|---|---|---|
| B1 | Centralize magic strings | Foundational refactoring | Low | — |
| B2 | Fix Lexer.error corruption | Engine fix | Low | — |
| B3 | `flip(axis)` op | Feature | Low | B1 |
| B4 | Multi-child rule bodies | Feature | Medium | B1 |
| B5 | Env-conditional rules | Feature | Medium | B1 |
| B6 | Colour lifting | Reverse path | Medium | — |
| B7 | Fix 18 xfailed grammars | Content | Medium | — |
| B8 | New grammars: castle, bridge | Content | Medium | B7 (pattern) |
| B9 | GLB viewer improvements | Rendering | Medium | — |

## Implementation waves

Wave 1 (parallel): B1, B2, B6, B7, B9 — no shared dependencies
Wave 2 (sequential after B1): B3, B4, B5 — depend on centralized names
Wave 3 (after B7): B8 — depends on xfail fixes for pattern reference