import os

import numpy as np
import pytest

from procedural_buildings.Processor import Processor
from procedural_buildings.Scope import Scope

GRAMMARS_DIR = "grammars"
SKIP_DIRS = {"_archive", "op_tests", "__pycache__"}
START_SCOPE = Scope.freshScope(np.array([0, 0, 0]), np.array([8, 8, 12]))

GRAMMAR_OVERRIDES = {
    "grammars/site_layout": ("block", (0, 0, 0, 40, 10, 20)),
    "grammars/warehouse_district": ("block", (0, 0, 0, 40, 10, 20)),
    "grammars/modern_district": ("block", (0, 0, 0, 40, 10, 30)),
    "grammars/engineered_garage": ("rule0", (0, 0, 0, 8, 8, 12)),
}

XFAIL_GRAMMARS = {
    "grammars/colour_blue",
    "grammars/fancy_building",
    "grammars/present",
    "grammars/rand_as_rule_priority",
    "grammars/rand_in_expr",
    "grammars/relative_split",
    "grammars/repeat_split_rand",
    "grammars/resize_move_colour",
    "grammars/rules_as_ops",
    "grammars/simple_comp",
    "grammars/simple_declaration",
    "grammars/simple_house",
    "grammars/simple_primitive",
    "grammars/simple_rand",
    "grammars/simple_repeat",
    "grammars/walled_house",
    "grammars/ends",
}


def _discover_grammars():
    for entry in sorted(os.listdir(GRAMMARS_DIR)):
        path = os.path.join(GRAMMARS_DIR, entry)
        if not os.path.isfile(path):
            continue
        if entry.startswith("."):
            continue
        yield path


@pytest.mark.parametrize("grammar_path", list(_discover_grammars()))
def test_grammar_renders(grammar_path, tmp_path):
    if grammar_path in XFAIL_GRAMMARS:
        pytest.xfail("Known-broken scratch grammar, will be deleted in cluster 3")

    override = GRAMMAR_OVERRIDES.get(grammar_path)
    if override:
        start_rule, scope_coords = override
        start_scope = Scope.freshScope(np.array(scope_coords[:3]), np.array(scope_coords[3:]))
    else:
        start_rule = "plot"
        start_scope = START_SCOPE

    p = Processor()
    p.grammarDir = ""
    out_path = str(tmp_path / "out.obj")
    p.grammarToManyObjs(grammar_path, start_rule, start_scope, 1, 0, out_path)
    assert os.path.exists(out_path), f"No OBJ written for {grammar_path}"
    assert os.path.getsize(out_path) > 0, f"Empty OBJ for {grammar_path}"
