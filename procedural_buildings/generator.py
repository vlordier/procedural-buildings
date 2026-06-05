import os
import random

import gin
import numpy as np

from .Processor import Processor
from .Scope import Scope

SHOWCASE_GRAMMARS = [
    {
        "name": "orthodox_church",
        "path": "grammars/orthodox_church",
        "materials": ["plaster", "roof_tile", "gold"],
        "complexity": "medium",
        "params": {},
        "start_rule": "plot",
        "start_scope": (0, 0, 0, 8, 8, 14),
    },
    {
        "name": "soviet_block",
        "path": "grammars/soviet_block",
        "materials": ["concrete", "glass"],
        "complexity": "high",
        "params": {"numFloors": 5, "floorHeight": 3},
        "start_rule": "plot",
        "start_scope": (0, 0, 0, 12, 8, 15),
    },
    {
        "name": "european_townhouse",
        "path": "grammars/european_townhouse",
        "materials": ["plaster", "roof_tile"],
        "complexity": "medium",
        "params": {},
        "start_rule": "plot",
        "start_scope": (0, 0, 0, 8, 8, 12),
    },
    {
        "name": "medieval_house",
        "path": "grammars/medieval_house",
        "materials": ["timber", "plaster", "roof_tile"],
        "complexity": "medium",
        "params": {},
        "start_rule": "plot",
        "start_scope": (0, 0, 0, 10, 8, 10),
    },
    {
        "name": "warehouse_district",
        "path": "grammars/warehouse_district",
        "materials": ["brick", "roof_tile", "glass"],
        "complexity": "high",
        "params": {},
        "start_rule": "block",
        "start_scope": (0, 0, 0, 40, 10, 20),
    },
    {
        "name": "modern_district",
        "path": "grammars/modern_district",
        "materials": ["glass", "metal", "plaster"],
        "complexity": "high",
        "params": {},
        "start_rule": "district",
        "start_scope": (0, 0, 0, 40, 10, 30),
    },
    {
        "name": "castle",
        "path": "grammars/castle",
        "materials": ["stone", "roof_tile"],
        "complexity": "high",
        "params": {"keepHeight": 12, "towerHeight": 8},
        "start_rule": "plot",
        "start_scope": (0, 0, 0, 20, 20, 20),
    },
    {
        "name": "bridge",
        "path": "grammars/bridge",
        "materials": ["stone"],
        "complexity": "low",
        "params": {"span": 12, "pillarW": 2},
        "start_rule": "plot",
        "start_scope": (0, 0, 0, 16, 4, 8),
    },
    {
        "name": "gin_demo",
        "path": "grammars/gin_demo",
        "materials": ["(gin-configured)"],
        "complexity": "medium",
        "params": {"panelR": 0.75},
        "start_rule": "plot",
        "start_scope": (0, 0, 0, 8, 8, 12),
    },
    {
        "name": "inset_demo",
        "path": "grammars/inset_demo",
        "materials": ["plaster"],
        "complexity": "low",
        "params": {},
        "start_rule": "plot",
        "start_scope": (0, 0, 0, 8, 8, 12),
    },
    {
        "name": "neighbor_facade",
        "path": "grammars/neighbor_facade",
        "materials": ["plaster", "roof_tile"],
        "complexity": "medium",
        "params": {},
        "start_rule": "plot",
        "start_scope": (0, 0, 0, 8, 8, 12),
    },
    {
        "name": "opening_demo",
        "path": "grammars/opening_demo",
        "materials": ["plaster", "glass"],
        "complexity": "medium",
        "params": {},
        "start_rule": "plot",
        "start_scope": (0, 0, 0, 8, 8, 12),
    },
]


class BuildingGenerator:
    def __init__(
        self,
        grammar: str,
        seed: int | None = None,
        materials: str | None = None,
        params: dict | None = None,
        start_rule: str = "plot",
        start_scope: tuple = (0, 0, 0, 8, 8, 12),
    ):
        self.grammar_path = os.path.abspath(grammar)
        self.start_rule = start_rule
        self.start_scope = Scope.freshScope(
            np.array(start_scope[:3]),
            np.array(start_scope[3:]),
        )
        self._metadata = self._parse_metadata()

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        gin_files = []
        gin_params = []
        if materials:
            gin_files.append(materials)
        if params:
            gin_params.append(f"grammar_var_overrides.values = {params}")
        gin.config.clear_config()
        gin.config.unlock_config()
        gin.parse_config_files_and_bindings(gin_files, gin_params)

    @classmethod
    def library(cls):
        return list(SHOWCASE_GRAMMARS)

    @classmethod
    def random(cls, seed=None, complexity=None, materials=None, params=None):
        import random as _random

        candidates = SHOWCASE_GRAMMARS
        if complexity:
            candidates = [g for g in candidates if g["complexity"] == complexity]
        if not candidates:
            candidates = SHOWCASE_GRAMMARS
        choice = _random.Random(seed).choice(candidates)
        merged_params = {**choice.get("params", {}), **(params or {})}
        return cls(
            grammar=choice["path"],
            seed=seed,
            materials=materials,
            params=merged_params if merged_params else None,
            start_rule=choice.get("start_rule", "plot"),
            start_scope=choice.get("start_scope", (0, 0, 0, 8, 8, 12)),
        )

    @classmethod
    def batch(cls, count, seed_start=0, materials=None, params=None, output_dir="buildings"):
        import os as _os

        _os.makedirs(output_dir, exist_ok=True)
        paths = []
        for i in range(count):
            gen = cls.random(seed=seed_start + i, materials=materials, params=params)
            path = _os.path.join(output_dir, f"building_{seed_start + i:04d}.glb")
            gen.to_glb(path)
            paths.append(path)
        return paths

    def to_glb(self, path: str):
        p = Processor()
        p.grammarDir = ""
        p.grammarToGlb(self.grammar_path, self.start_rule, self.start_scope, path)

    def to_obj(self, path: str):
        p = Processor()
        p.grammarDir = ""
        p.grammarToManyObjs(self.grammar_path, self.start_rule, self.start_scope, 1, 0, path)

    def get_metadata(self) -> dict:
        return self._metadata

    def _parse_metadata(self) -> dict:
        meta = {"materials": [], "params": {}, "complexity": "unknown"}
        try:
            with open(self.grammar_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("# @meta"):
                        continue
                    if not line.startswith("# "):
                        break
                    content = line[2:].strip()
                    if content.startswith("materials:"):
                        meta["materials"] = [m.strip() for m in content[10:].split(",")]
                    elif content.startswith("params:"):
                        for p in content[8:].split(","):
                            p = p.strip()
                            if "=" in p:
                                k, v = p.split("=", 1)
                                meta["params"][k.strip()] = v.strip()
                    elif content.startswith("complexity:"):
                        meta["complexity"] = content[11:].strip()
        except FileNotFoundError:
            pass
        return meta
