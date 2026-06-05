import math
import random
from dataclasses import dataclass, field


@dataclass
class LayoutData:
    blocks: list[list[tuple[float, float]]] = field(default_factory=list)
    roads: list[list[tuple[float, float]]] = field(default_factory=list)
    block_zones: list[str] = field(default_factory=list)
    features: dict = field(default_factory=dict)


class MedievalLayout:
    def __init__(self, seed: int = None, size: str = "medium"):
        self.rng = random.Random(seed)
        self.size = size
        self.radius = {"small": 100, "medium": 200, "large": 400}[size]
        self.num_radials = self.rng.randint(4, 8)

    def generate(self) -> LayoutData:
        min_gap = math.radians(30)
        max_gap = math.radians(90)

        gaps = [self.rng.uniform(min_gap, max_gap) for _ in range(self.num_radials)]
        total = sum(gaps)
        norm_gaps = [2.0 * math.pi * g / total for g in gaps]

        cum_angles = []
        a = 0.0
        for g in norm_gaps:
            a += g
            cum_angles.append(a)

        offset = self.rng.random() * 2.0 * math.pi
        cum_angles = sorted((a + offset) % (2.0 * math.pi) for a in cum_angles)

        num_rings = self.rng.randint(2, 4)
        ring_radii = []
        for i in range(1, num_rings + 1):
            base_r = i * self.radius / (num_rings + 1)
            r = base_r * self.rng.uniform(0.9, 1.1)
            ring_radii.append(r)
        ring_radii.sort()

        n = len(cum_angles)

        radial_roads = []
        for angle in cum_angles:
            pts = [(0.0, 0.0), (self.radius * math.cos(angle), self.radius * math.sin(angle))]
            radial_roads.append(pts)

        ring_roads = []
        for rr in ring_radii:
            pts = []
            for angle in cum_angles:
                d = self.rng.uniform(0.95, 1.05)
                r = rr * d
                pts.append((r * math.cos(angle), r * math.sin(angle)))
            pts.append(pts[0])
            ring_roads.append(pts)

        roads = radial_roads + ring_roads
        blocks = []
        block_zones = []

        center_radius = ring_radii[0] * 0.35
        center_poly = []
        num_cseg = 16
        for k in range(num_cseg):
            angle = 2.0 * math.pi * k / num_cseg
            center_poly.append((center_radius * math.cos(angle), center_radius * math.sin(angle)))
        blocks.append(center_poly)
        block_zones.append("downtown")

        def arc(r, a1, a2, steps=4):
            pts = []
            for t in range(steps + 1):
                frac = t / steps
                angle = a1 + (a2 - a1) * frac
                pts.append((r * math.cos(angle), r * math.sin(angle)))
            return pts

        for i in range(n):
            a1 = cum_angles[i]
            a2 = cum_angles[(i + 1) % n]
            poly = arc(center_radius, a1, a2) + list(reversed(arc(ring_radii[0], a1, a2)))
            blocks.append(poly)
            block_zones.append("downtown")

        for ri in range(len(ring_radii) - 1):
            r_inner = ring_radii[ri]
            r_outer = ring_radii[ri + 1]
            for i in range(n):
                a1 = cum_angles[i]
                a2 = cum_angles[(i + 1) % n]
                poly = arc(r_inner, a1, a2) + list(reversed(arc(r_outer, a1, a2)))
                blocks.append(poly)
                block_zones.append("commercial" if ri == 0 else "residential")

        wall_radius = self.radius * 1.05
        for i in range(n):
            a1 = cum_angles[i]
            a2 = cum_angles[(i + 1) % n]
            poly = arc(ring_radii[-1], a1, a2) + list(reversed(arc(wall_radius, a1, a2)))
            blocks.append(poly)
            block_zones.append("residential")

        wall_pts = []
        for k in range(36):
            angle = 2.0 * math.pi * k / 36
            wall_pts.append((wall_radius * math.cos(angle), wall_radius * math.sin(angle)))

        features = {
            "cathedral": (0.0, 0.0),
            "square": (0.0, 0.0),
            "gates": [(wall_radius * math.cos(a), wall_radius * math.sin(a)) for a in cum_angles],
            "wall": wall_pts,
        }

        return LayoutData(blocks=blocks, roads=roads, block_zones=block_zones, features=features)


class GridLayout:
    def __init__(self, seed: int = None, size: str = "medium"):
        self.rng = random.Random(seed)
        self.size = size
        dims = {"small": (4, 4), "medium": (8, 6), "large": (16, 12)}
        self.rows, self.cols = dims[size]

    def generate(self) -> LayoutData:
        block_w = 100.0
        block_d = 60.0
        street_w = 10.0
        avenue_w = 20.0

        def street_width(idx):
            return avenue_w if (idx > 0 and idx % 4 == 0) else street_w

        total_w = self.cols * block_w + sum(street_width(c) for c in range(self.cols + 1))
        total_d = self.rows * block_d + sum(street_width(r) for r in range(self.rows + 1))

        offsets_x = []
        x = -total_w / 2.0
        for c in range(self.cols + 1):
            offsets_x.append(x)
            x += street_width(c) + block_w

        offsets_z = []
        z = -total_d / 2.0
        for r in range(self.rows + 1):
            offsets_z.append(z)
            z += street_width(r) + block_d

        blocks = []
        block_zones = []

        center_r = (self.rows - 1) / 2.0
        center_c = (self.cols - 1) / 2.0

        for row in range(self.rows):
            for col in range(self.cols):
                bx = offsets_x[col] + street_width(col)
                bz = offsets_z[row] + street_width(row)

                w = block_w * self.rng.uniform(0.95, 1.05)
                d = block_d * self.rng.uniform(0.95, 1.05)

                cx = bx + block_w / 2.0
                cz = bz + block_d / 2.0

                poly = [
                    (cx - w / 2.0, cz - d / 2.0),
                    (cx + w / 2.0, cz - d / 2.0),
                    (cx + w / 2.0, cz + d / 2.0),
                    (cx - w / 2.0, cz + d / 2.0),
                ]
                blocks.append(poly)

                dr = abs(row - center_r) / self.rows
                dc = abs(col - center_c) / self.cols
                dist = max(dr, dc)

                if dist < 0.25:
                    block_zones.append("downtown")
                elif dist < 0.5:
                    block_zones.append("midrise")
                else:
                    block_zones.append("residential")

        roads = []
        for row in range(self.rows + 1):
            z_center = offsets_z[row] + street_width(row) / 2.0
            roads.append([(-total_w / 2.0, z_center), (total_w / 2.0, z_center)])

        for col in range(self.cols + 1):
            x_center = offsets_x[col] + street_width(col) / 2.0
            roads.append([(x_center, -total_d / 2.0), (x_center, total_d / 2.0)])

        margin = 30.0
        freeway = [
            (-total_w / 2.0 - margin, -total_d / 2.0 - margin),
            (total_w / 2.0 + margin, total_d / 2.0 + margin),
        ]
        roads.append(freeway)

        return LayoutData(blocks=blocks, roads=roads, block_zones=block_zones, features={"freeway": freeway})
