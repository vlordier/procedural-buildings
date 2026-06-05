# Cluster 1: Test Infrastructure — Index

**Cluster goal:** Make the engine's correctness verifiable. Add the missing test
surface so that future features and refactors ship with confidence, not anxiety.

**Why this cluster first:** Every other improvement (engine hardening, grammar
cleanup, dev tooling) is unsafe to do without tests. The current 10-test
suite covers only the recent `scope_env` refactor. The parser, ops, simplify
machinery, Scope methods, and the entire reverse-engineering path are
untested.

---

## Items in this cluster

| # | Design doc | What it adds | Risk |
|---|---|---|---|
| 1.1 | `2026-06-05-...-test-grammars-design.md` | `tests/test_grammars.py` — auto-discovers every `grammars/**` (except `_archive/`) and renders each to a tempfile | Low |
| 1.2 | `2026-06-05-...-cli-seed-design.md` | `--seed N` flag for reproducible builds | Low |
| 1.3 | `2026-06-05-...-cli-validate-design.md` | `--validate` flag: parse + simplify only, no `.obj` write | Low |
| 1.4 | `2026-06-05-...-op-tests-pytest-design.md` | Wire `grammars/op_tests/*` into pytest as a feature catalogue | Low |
| 1.5 | `2026-06-05-...-boxsplitter-roundtrip-design.md` | `tests/test_round_trip.py` — vertex-set equality round-trip for showcase grammars | Medium |
| 1.6 | `2026-06-05-...-golden-snapshots-design.md` | `tests/test_golden.py` — hash snapshots of 5 reference grammars | Low |

## Dependency graph

```
1.1 test_grammars         (no deps)
1.2 cli --seed            (no deps)
1.3 cli --validate        (no deps)
1.4 op_tests→pytest       (depends on 1.1 — reuses the render harness)
1.5 round-trip            (depends on 1.1 — reuses the render harness)
1.6 golden                (depends on 1.2 — golden needs deterministic CLI; or set seed inside test)
```

## Implementation order

Wave 1 (parallel, no deps): 1.1, 1.2, 1.3
Wave 2: 1.4 (after 1.1)
Wave 3 (parallel): 1.5 (after 1.1), 1.6 (after 1.2; or set seed in-process)

## Acceptance for the cluster

- `pytest tests/` runs the existing 10 tests + ~80 new tests.
- Every grammar in `grammars/` (excluding `_archive/`) renders without error.
- Every grammar in `grammars/op_tests/` renders without error.
- Showcase grammars survive a round-trip (build → reverse → build → same vertices).
- 5 reference grammars have stable golden hashes.
- `--seed N` produces byte-identical output across runs.
- `--validate` exits 0 on a valid grammar, non-zero on a broken one.

## Out of scope (covered in later clusters)

- Op unit tests, parser tests, Scope tests, simplify tests → **Cluster 2**
- Grammar cleanup, README files for grammars/configs → **Cluster 3**
- Makefile, ARCHITECTURE.md, type hints, dev tooling → **Cluster 4**
- Colour round-trip fix in `ObjReader`/`BoxSplitter` → **Cluster 2** (1.5
  currently asserts vertex equality only; once cluster 2 lands the
  engine-native colour recovery, 1.5 can be tightened to a colour-aware
  comparison)
