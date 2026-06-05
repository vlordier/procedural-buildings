class GeometryAccumulator:
    def __init__(self):
        self.positions = []
        self.normals = []
        self.uvs = []
        self.indices = []
        self.material_names = []
        self.vertex_count = 0
        self.current_material = None

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
        for face in prim.faceData:
            for vert_data in face:
                idx = int(vert_data[0]) - 1
                self.indices.append(base + idx)
        if self.current_material:
            self.material_names.append(self.current_material)
        self.vertex_count += len(verts)

    def reset(self):
        self.positions = []
        self.normals = []
        self.uvs = []
        self.indices = []
        self.material_names = []
        self.vertex_count = 0
        self.current_material = None

    def material(self, name):
        self.current_material = name
