import hashlib
import json
import os
import random

import gin
import numpy as np
import pytest

from procedural_buildings.Processor import Processor
from procedural_buildings.Scope import Scope

GOLDEN_DIR = "tests/golden"
HASH_FILE = os.path.join(GOLDEN_DIR, "hashes.json")

REFERENCE = [
    ("orthodox_church", "grammars/orthodox_church", "plot", (0, 0, 0, 8, 8, 14), None),
    ("soviet", "grammars/soviet_block", "plot", (0, 0, 0, 12, 8, 15), None),
    ("material_solid", "grammars/material_building", "plot", (0, 0, 0, 8, 8, 12), None),
    ("material_checker", "grammars/material_building", "plot", (0, 0, 0, 8, 8, 12), "configs/checker.gin"),
]


def _canonicalise_obj(path):
    lines = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            lines.append(line)
    return "\n".join(sorted(lines)).encode("utf-8")


def _hash_file(path):
    return hashlib.sha256(_canonicalise_obj(path)).hexdigest()


def _load_hashes():
    if not os.path.exists(HASH_FILE):
        return {}
    with open(HASH_FILE) as f:
        return json.load(f)


@pytest.mark.parametrize("ref_id,grammar,rule,scope,gin_file", REFERENCE)
def test_golden_hash(ref_id, grammar, rule, scope, gin_file, tmp_path):
    random.seed(42)
    np.random.seed(42)
    gin.clear_config()

    start_scope = Scope.freshScope(np.array(scope[:3]), np.array(scope[3:]))

    if gin_file:
        gin.parse_config_files_and_bindings([gin_file], [])

    p = Processor()
    p.grammarDir = ""
    out = str(tmp_path / "out.obj")
    p.grammarToManyObjs(grammar, rule, start_scope, 1, 0, out)

    new_hash = _hash_file(out)
    stored = _load_hashes().get(ref_id)

    if stored is None:
        pytest.skip(f"No stored hash for {ref_id}; computed {new_hash[:12]}...")
    assert new_hash == stored, (
        f"Golden hash mismatch for {ref_id}:\n"
        f"  expected: {stored[:12]}\n"
        f"  got:      {new_hash[:12]}\n"
        f"If this change is intentional, run scripts/update_golden.py"
    )
