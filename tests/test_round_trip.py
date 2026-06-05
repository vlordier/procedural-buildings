import os

import numpy as np
import pytest

from procedural_buildings.Processor import Processor
from procedural_buildings.Scope import Scope

SHOWCASE = [
    ("grammars/op_tests/split", "plot", (0, 0, 0, 8, 8, 12)),
    ("grammars/op_tests/repeatN", "plot", (0, 0, 0, 8, 8, 12)),
    ("grammars/cabin", "plot", (0, 0, 0, 8, 8, 12)),
]

TOLERANCE = 4


def _parse_obj_vertices(path):
    verts = []
    with open(path) as f:
        for line in f:
            if line.startswith("v "):
                parts = line.split()
                if len(parts) >= 4:
                    x, y, z = parts[1], parts[2], parts[3]
                    verts.append((
                        round(float(x), TOLERANCE),
                        round(float(y), TOLERANCE),
                        round(float(z), TOLERANCE),
                    ))
    return frozenset(verts)


@pytest.mark.parametrize("grammar_path,start_rule,scope", SHOWCASE)
def test_round_trip_preserves_geometry(grammar_path, start_rule, scope, tmp_path):
    start_scope = Scope.freshScope(np.array(scope[:3]), np.array(scope[3:]))

    # Build 1
    p1 = Processor()
    p1.grammarDir = ""
    out1 = str(tmp_path / "first.obj")
    p1.grammarToManyObjs(grammar_path, start_rule, start_scope, 1, 0, out1)
    v1 = _parse_obj_vertices(out1)
    assert len(v1) > 0, f"No vertices in {out1}"

    # Reverse
    reverse_dir = str(tmp_path / "reverse")
    p2 = Processor()
    p2.engineeredDir = reverse_dir + "/"
    p2.objsToGrammar([out1], "rebuilt_grammar")

    # Rebuild
    p3 = Processor()
    p3.grammarDir = ""
    out3 = str(tmp_path / "second.obj")
    p3.grammarToManyObjs(os.path.join(reverse_dir, "rebuilt_grammar"), "rule0", start_scope, 1, 0, out3)
    v2 = _parse_obj_vertices(out3)
    assert len(v2) > 0, f"No vertices in {out3}"

    missing = v1 - v2
    extra = v2 - v1
    assert not missing, f"{len(missing)} vertices lost in round-trip for {grammar_path}"
    assert not extra, f"{len(extra)} vertices added in round-trip for {grammar_path}"
