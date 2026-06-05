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
