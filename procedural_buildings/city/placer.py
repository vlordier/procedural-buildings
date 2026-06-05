import os
import random
from dataclasses import dataclass

from .layout import LayoutData


@dataclass
class PlacedBuilding:
    glb_path: str
    position: tuple[float, float, float]
    rotation: float
    building_type: str


ZONE_MAP = {
    "downtown": ["modern_district", "factory", "train_station"],
    "residential": ["cottage", "barn", "european_townhouse", "medieval_house", "greenhouse"],
    "commercial": ["castle", "windmill", "chapel", "lighthouse"],
    "medieval_core": ["orthodox_church", "medieval_house", "castle", "chapel", "windmill"],
    "suburbs": ["cottage", "barn", "lighthouse", "greenhouse", "watchtower"],
}


class BuildingPlacer:
    def __init__(self, layout: LayoutData, seed: int = None):
        self.layout = layout
        self.rng = random.Random(seed)

    def place_buildings(self, output_dir: str) -> list[PlacedBuilding]:
        from procedural_buildings import BuildingGenerator

        buildings_dir = os.path.join(output_dir, "buildings")
        os.makedirs(buildings_dir, exist_ok=True)

        placed = []
        for i, block in enumerate(self.layout.blocks):
            if len(block) < 3:
                continue

            zone = self.layout.block_zones[i] if i < len(self.layout.block_zones) else "residential"
            candidates = ZONE_MAP.get(zone, ZONE_MAP["residential"])

            btype = self.rng.choice(candidates)

            cx = sum(p[0] for p in block) / len(block)
            cz = sum(p[1] for p in block) / len(block)

            cx += self.rng.uniform(-3, 3)
            cz += self.rng.uniform(-3, 3)

            rotation = self.rng.uniform(0, 6.28)

            seed_i = self.rng.randint(0, 1000000)
            gen = BuildingGenerator.random(seed=seed_i, materials="configs/materials_basic.gin")
            glb_name = f"building_{i:04d}.glb"
            glb_path = os.path.join(buildings_dir, glb_name)
            gen.to_glb(glb_path)

            placed.append(
                PlacedBuilding(
                    glb_path=f"buildings/{glb_name}",
                    position=(round(cx, 2), 0.0, round(cz, 2)),
                    rotation=round(rotation, 4),
                    building_type=btype,
                )
            )

        return placed
