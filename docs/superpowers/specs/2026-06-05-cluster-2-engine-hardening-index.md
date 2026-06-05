# Cluster 2: Engine Hardening — Index

**Cluster goal:** Fill the engine's internal test gap. The parser, ops,
simplify machinery, Scope methods, and the entire reverse-engineering
colour path are untested. Add unit tests for each subsystem and fix the
lossy colour round-trip in the reverse path.

**Why this cluster next:** Cluster 1 proved the grammar render pipeline
works (58 tests pass). Now we need white-box tests for the engine itself
so that future engine changes (new ops, refactors, colour lifting) don't
introduce regressions. The colour round-trip fix is the highest-value
production change — it makes the project's signature feature (reverse
engineering) actually preserve colour, and improves the round-trip test
from 3 simple grammars to all showcase grammars.

**What changed from the original cluster 2 spec (pre-cluster 1):**
- Lexer already has `ignore_comment = r"\#.*"` — no Lexer changes needed
- The colour bug is purely in `ObjReader` (uses `lines[0]` verbatim as
  primName, including the `# colour(...)` suffix) and `Box` (no colour attr)
- Leaf-level OpColour wrapping was chosen (simpler, no post-processing pass)
- `scripts/obj_to_glb_colored.py` is deleted — the engine is the source of truth

---

## Items in this cluster

| # | Design doc | What it adds | Risk |
|---|---|---|---|
| 2.1 | `2026-06-05-parser-tests-design.md` | `tests/test_parser.py` — Lexer, GrammarParser, Checker, GrammarVars tests | Low |
| 2.2 | `2026-06-05-op-tests-design.md` | `tests/test_ops.py` — unit test for each of 16 Op subclasses | Low |
| 2.3 | `2026-06-05-simplify-tests-design.md` | `tests/test_simplify.py` — Args.combineArgs, Op.simplify, Op.combineMany | Low |
| 2.4 | `2026-06-05-scope-tests-design.md` | `tests/test_scope.py` — Scope.split, repeat, repeatN, comp, inset, opening, translate, rotate | Low |
| 2.5 | `2026-06-05-colour-roundtrip-design.md` | Fix ObjReader + Box for colour; delete scripts/obj_to_glb_colored.py; tests/test_colour.py | Medium |

## Dependency graph

All 5 items are independent — no item waits on another. Each modifies
different files. Items 2.1–2.4 are pure test additions (no production
code changes). Item 2.5 modifies 2 production files + deletes 1 script.

## Implementation order

All 5 items can run in parallel.

## Acceptance for the cluster

- `pytest tests/` runs all cluster 1 (87 existing) + cluster 2 new tests
- Every Op subclass has a unit test with a minimal run assertion
- Parser tests cover Lexer token types, `#` comments, valid/invalid grammar
  parse, Checker validation, and GrammarVars expression
- Simplify tests cover all type combinations in `Args.combineArgs` and
  the main merge paths in `Op.simplify` / `Op.combineMany`
- Scope tests cover every public method: split, repeat, repeatN, comp,
  inset, opening, translate, rotate
- Colour round-trip: build coloured grammar → reverse → rebuild →
  same vertices AND same colour-bearing primitives
- `scripts/obj_to_glb_colored.py` is deleted (no longer needed)
- Showcase grammars (orthodox_church, soviet_block) now pass the
  round-trip test

## Out of scope (covered in later clusters)

- Grammar archive/cleanup → **Cluster 3**
- Dev tooling (Makefile, ARCHITECTURE.md, type hints) → **Cluster 4**
- Fixing Lexer.error silent-corruption bug (separate concern, not blocking)