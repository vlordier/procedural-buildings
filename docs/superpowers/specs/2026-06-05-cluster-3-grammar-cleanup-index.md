# Cluster 3: Grammar Cleanup — Index

**Cluster goal:** Clean up the grammar directory from junk-drawer state to
curated catalogue. Archive duplicate/iterative/broken grammars to
`_archive/`, add READMEs for grammars and configs, update test xfail
lists to match the new directory state.

| # | Item | Action |
|---|---|---|
| 3.1 | Archive 16 grammars | Move 12 duplicates + 4 scratches to `grammars/_archive/` |
| 3.2 | `grammars/README.md` | Document showcase vs op_tests vs _archive, how to add |
| 3.3 | `configs/README.md` | Document gin-config feature and 5 configs |
| 3.4 | Update test xfail lists | Remove archived paths from `XFAIL_GRAMMARS` in test_grammars.py |

## Archive list (16 files)

- `also_nice_house` — iterative house
- `amazing_house` — iterative house
- `better_house` — iterative house
- `cabin` — broken primitive references
- `foo` — broken syntax (uses `/`)
- `home` — iterative house
- `home_new_grammar_style` — iterative house
- `house_with_garage` — iterative house
- `house_with_garage2` — iterative house
- `house_with_garage3` — iterative house
- `house_with_prims` — iterative house
- `nice_house` — iterative house
- `nice_roof_house` — iterative house
- `nice_roofs_2` — iterative house
- `overlap` — undocumented behavior exploit
- `window` — broken primitive reference (quoted `I('window')`)

## Acceptance

- `ls grammars/` is curated — no obvious junk
- `ls grammars/_archive/` contains the 16 archived grammars
- `pytest tests/` passes with xfail count reduced by 16 (from 29 to 13)
- A new contributor can read `grammars/README.md` and understand the layout
- A new contributor can read `configs/README.md` and use gin-config