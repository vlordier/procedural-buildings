import os

from .layout import LayoutData
from .placer import PlacedBuilding


class UsdSceneWriter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def write(self, layout: LayoutData, buildings: list[PlacedBuilding]):
        lines = []
        lines.append("#usda 1.0")
        lines.append("")

        gs = self._get_ground_size(layout)
        lines.append('def Xform "World" {')
        lines.append('    def Mesh "Ground" {')
        lines.append(
            f"        float3[] points = [({-gs}, 0, {-gs}), ({gs}, 0, {-gs}), ({gs}, 0, {gs}), ({-gs}, 0, {gs})]"
        )
        lines.append("        int[] faceVertexCounts = [4]")
        lines.append("        int[] faceVertexIndices = [0, 1, 2, 3]")
        lines.append('        uniform token subdivisionScheme = "none"')
        lines.append("    }")
        lines.append("")

        if layout.roads:
            lines.append('    def Xform "Roads" {')
            for i, road in enumerate(layout.roads):
                if len(road) < 2:
                    continue
                pts_str = ", ".join(f"({x}, 0.02, {z})" for x, z in road)
                idx_str = ", ".join(str(j) for j in range(len(road)))
                lines.append(f'        def Mesh "Road_{i:04d}" {{')
                lines.append(f"            float3[] points = [{pts_str}]")
                lines.append(f"            int[] faceVertexCounts = [{len(road)}]")
                lines.append(f"            int[] faceVertexIndices = [{idx_str}]")
                lines.append("        }")
            lines.append("    }")
            lines.append("")

        lines.append('    def Xform "Buildings" {')
        for i, b in enumerate(buildings):
            name = f"building_{i:04d}"
            lines.append(f'        def Xform "{name}" (')
            lines.append(f"            prepend references = @./{b.glb_path}@")
            lines.append("        ) {")
            lines.append(f"            double3 xformOp:translate = ({b.position[0]}, {b.position[1]}, {b.position[2]})")
            lines.append(f"            double3 xformOp:rotateXYZ = (0, {b.rotation * 57.3:.1f}, 0)")
            lines.append('            uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateXYZ"]')
            lines.append("        }")
        lines.append("    }")

        lines.append("}")

        usda_path = os.path.join(self.output_dir, "city.usda")
        with open(usda_path, "w") as f:
            f.write("\n".join(lines))
        return usda_path

    def _get_ground_size(self, layout):
        m = 50
        for block in layout.blocks:
            for x, z in block:
                m = max(m, abs(x) + 10, abs(z) + 10)
        return m
