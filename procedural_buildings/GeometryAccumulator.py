from .Primitive import basicPrims


class GeometryAccumulator:
    def __init__(self, prims=basicPrims):
        self.positions = []
        self.normals = []
        self.uvs = []
        self.indices = []
        self.material_names = []
        self._colour_materials = {}
        self.vertex_count = 0
        self.current_material = None
        self.prims = prims

    def add_primitive(self, prim, scope):
        verts = scope.putVertsInScope(prim.verts, prim.boundingBox)
        base = self.vertex_count
        for v in verts:
            self.positions.append([float(v[0]), float(v[1]), float(v[2])])
        if hasattr(prim, "uvs") and prim.uvs:
            for uv in prim.uvs:
                self.uvs.append([float(uv[0]), float(uv[1])])
        if hasattr(prim, "normals") and prim.normals:
            for n in prim.normals:
                self.normals.append([float(n[0]), float(n[1]), float(n[2])])
        face_count = 0
        for face in prim.faceData:
            for vert_data in face:
                idx = int(vert_data[0]) - 1
                self.indices.append(base + idx)
            face_count += 1
        mat = self.current_material
        for _ in range(face_count):
            self.material_names.append(mat)
        self.vertex_count += len(verts)

    def addPrim(self, primName, scope):
        if primName not in self.prims:
            prim = self.prims.get("rect", list(self.prims.values())[0])
        else:
            prim = self.prims[primName]
        self.add_primitive(prim, scope)

    def colour(self, col, scope):
        r, g, b = col[0], col[1], col[2]
        name = f"col_{r:.2f}_{g:.2f}_{b:.2f}"
        self._colour_materials[name] = [r, g, b]
        self.current_material = name

    def reset(self):
        self.positions = []
        self.normals = []
        self.uvs = []
        self.indices = []
        self.material_names = []
        self._colour_materials = {}
        self.vertex_count = 0
        self.current_material = None

    def material(self, name):
        self.current_material = name
