import os
import pytest
import numpy as np
from procedural_buildings.Processor import Processor
from procedural_buildings.Scope import Scope

OP_TESTS_DIR = "grammars/op_tests"
START_SCOPE = Scope.freshScope(np.array([0, 0, 0]), np.array([8, 8, 12]))

# Grammars that test features not yet supported by the parser
XFAIL_OP_TESTS = {
    "grammars/op_tests/params",  # parser can't handle IDENT LPAR in split body (size vs op ambiguity)
}


def _discover_op_tests():
    for name in sorted(os.listdir(OP_TESTS_DIR)):
        path = os.path.join(OP_TESTS_DIR, name)
        if os.path.isfile(path):
            yield path


@pytest.mark.parametrize("grammar_path", list(_discover_op_tests()))
def test_op_test_renders(grammar_path, tmp_path):
    if grammar_path in XFAIL_OP_TESTS:
        pytest.xfail("Feature not yet supported by the parser")

    p = Processor()
    p.grammarDir = ""
    out_path = str(tmp_path / "out.obj")
    p.grammarToManyObjs(grammar_path, "plot", START_SCOPE, 1, 0, out_path)
    assert os.path.exists(out_path), f"No OBJ written for {grammar_path}"
    assert os.path.getsize(out_path) > 0, f"Empty OBJ for {grammar_path}"