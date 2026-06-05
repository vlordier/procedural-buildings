import os
import random

import gin
import numpy as np

from .Processor import Processor
from .Scope import Scope


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
        gin.parse_config_files_and_bindings(gin_files, gin_params)

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
