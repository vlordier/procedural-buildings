import random as _random

import gin


@gin.configurable
def material_presets(values=None):
    return values or {}


def get_material(name):
    presets = material_presets()
    return presets.get(
        name,
        {
            "base_color": [0.7, 0.7, 0.7, 1.0],
            "roughness": 0.5,
            "metallic": 0.0,
        },
    )


MATERIAL_PALETTES = {
    "stone": [
        [0.60, 0.55, 0.50],
        [0.70, 0.60, 0.50],
        [0.55, 0.50, 0.45],
        [0.80, 0.60, 0.30],
        [0.75, 0.70, 0.65],
    ],
    "brick": [
        [0.70, 0.30, 0.20],
        [0.60, 0.25, 0.15],
        [0.75, 0.40, 0.25],
        [0.55, 0.35, 0.20],
    ],
    "roof_tile": [
        [0.40, 0.25, 0.20],
        [0.30, 0.15, 0.10],
        [0.50, 0.30, 0.20],
        [0.35, 0.25, 0.20],
    ],
    "plaster": [
        [0.85, 0.82, 0.78],
        [0.90, 0.85, 0.75],
        [0.80, 0.75, 0.70],
        [0.92, 0.88, 0.82],
        [0.75, 0.72, 0.68],
    ],
    "wood": [
        [0.55, 0.35, 0.15],
        [0.45, 0.28, 0.12],
        [0.60, 0.40, 0.20],
        [0.50, 0.30, 0.10],
    ],
    "glass": [
        [0.60, 0.70, 0.80],
        [0.50, 0.60, 0.70],
        [0.70, 0.80, 0.90],
        [0.80, 0.80, 0.85],
    ],
    "concrete": [
        [0.75, 0.73, 0.70],
        [0.70, 0.65, 0.60],
        [0.65, 0.68, 0.72],
        [0.80, 0.78, 0.75],
    ],
    "metal": [
        [0.50, 0.50, 0.50],
        [0.60, 0.55, 0.50],
        [0.70, 0.70, 0.72],
        [0.40, 0.42, 0.45],
    ],
    "gold": [
        [0.90, 0.75, 0.30],
        [0.85, 0.70, 0.25],
    ],
    "timber": [
        [0.50, 0.30, 0.15],
        [0.60, 0.40, 0.20],
        [0.45, 0.25, 0.10],
    ],
}


def random_material_presets(material_names, seed=None):
    rng = _random.Random(seed)
    presets = {}
    for name in material_names:
        palette = MATERIAL_PALETTES.get(name)
        if palette:
            bc = list(rng.choice(palette))
            presets[name] = {
                "base_color": bc + [1.0],
                "roughness": rng.uniform(0.3, 0.9),
                "metallic": rng.choice([0.0, 0.0, 0.0, 0.1, 0.3]),
            }
    return presets
