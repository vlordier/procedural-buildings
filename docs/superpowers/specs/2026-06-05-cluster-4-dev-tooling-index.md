# Cluster 4: Dev Tooling & Docs — Index

**Cluster goal:** Make the project pleasant to work in for the next
contributor (including future-you). Add a Makefile, architecture doc,
current README, fix docs, and basic type hints on the public surface.

| # | Item | Files |
|---|---|---|
| 4.1 | Makefile | Create: `Makefile` |
| 4.2 | ARCHITECTURE.md | Create: `docs/ARCHITECTURE.md` |
| 4.3 | README sync | Modify: `README.md` |
| 4.4 | Move how_to doc | Delete: `procedural_buildings/how_to_add_a_new_operation.txt`; Create: `docs/how_to_add_a_new_operation.md` |
| 4.5 | Type hints | Modify: `Scope.py`, `Ops.py`, `ContextObj.py`, `Primitive.py`, `ObjReader.py`, `BoxSplitter.py` |

## Acceptance

- `make test` runs the full pytest suite
- `make lint` runs ruff check
- `make example` renders a showcase grammar
- `docs/ARCHITECTURE.md` explains the data flow at a glance
- `README.md` is current: removed "uni project" tag, removed deleted grammar refs, added showcase grammars + gin-config
- `procedural_buildings/how_to_add_a_new_operation.txt` is gone; `docs/how_to_add_a_new_operation.md` exists with scope_env contract and test step
- Public methods on Scope, Op, Args, ContextObj, Primitive, ObjReader, BoxSplitter have basic type annotations