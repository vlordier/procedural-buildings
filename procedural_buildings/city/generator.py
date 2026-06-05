from .layout import GridLayout, MedievalLayout
from .placer import BuildingPlacer
from .writer import UsdSceneWriter


class CityGenerator:
    def __init__(self, style="medieval", seed=None, size="medium"):
        self.style = style
        self.seed = seed
        self.size = size

    def generate(self, output_dir):
        import os

        os.makedirs(output_dir, exist_ok=True)

        layout_cls = {"medieval": MedievalLayout, "grid": GridLayout}[self.style]
        layout = layout_cls(seed=self.seed, size=self.size).generate()

        placer = BuildingPlacer(layout, seed=self.seed)
        buildings = placer.place_buildings(output_dir)

        writer = UsdSceneWriter(output_dir)
        usda_path = writer.write(layout, buildings)

        return usda_path
