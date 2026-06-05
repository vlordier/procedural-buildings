#!/usr/bin/env python3
import json
import os
import random
import sys

import gin
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tests.test_golden import REFERENCE, _hash_file, GOLDEN_DIR
from procedural_buildings.Processor import Processor
from procedural_buildings.Scope import Scope

random.seed(42)
np.random.seed(42)

hashes = {}
for ref_id, grammar_file, rule, scope, gin_file in REFERENCE:
    gin.clear_config()
    start_scope = Scope.freshScope(np.array(scope[:3]), np.array(scope[3:]))
    if gin_file:
        gin.parse_config_files_and_bindings([gin_file], [])
    p = Processor()
    p.grammarDir = ""
    out = "/tmp/golden_out.obj"
    p.grammarToManyObjs(grammar_file, rule, start_scope, 1, 0, out)
    h = _hash_file(out)
    hashes[ref_id] = h
    print(f"{ref_id}: {h[:12]}...")

os.makedirs(GOLDEN_DIR, exist_ok=True)
with open(os.path.join(GOLDEN_DIR, "hashes.json"), "w") as f:
    json.dump(hashes, f, indent=2, sort_keys=True)
    f.write("\n")
print(f"Wrote {GOLDEN_DIR}/hashes.json")