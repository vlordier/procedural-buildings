"""View a city USD scene by reading the USD text format and rendering with pyglet."""
import json
import os
import re
import struct
import sys

import numpy as np
from pyglet import app, clock, graphics, window
from pyglet.gl import *

VERTEX_SHADER = """
#version 120
attribute vec3 position;
attribute vec3 normal;
attribute vec2 texcoord;
uniform mat4 modelview;
uniform mat4 projection;
uniform mat3 normal_matrix;
uniform vec3 light_dir;
varying vec3 v_normal;
varying vec2 v_texcoord;
void main() {
    gl_Position = projection * modelview * vec4(position, 1.0);
    v_normal = normalize(normal_matrix * normal);
    v_texcoord = texcoord;
}
"""

FRAGMENT_SHADER = """
#version 120
varying vec3 v_normal;
varying vec2 v_texcoord;
uniform vec3 base_color;
uniform float roughness;
void main() {
    vec3 light = normalize(vec3(0.5, 1.0, 0.3));
    float diff = max(0.0, dot(v_normal, light)) * 0.7 + 0.3;
    gl_FragColor = vec4(base_color * diff, 1.0);
}
"""


def read_usda(path):
    """Parse our simple USD format to extract references + transforms."""
    buildings = []
    ground = None
    with open(path) as f:
        text = f.read()

    base_dir = os.path.dirname(os.path.abspath(path))

    # Find ground
    m = re.search(r"points = \[([^\]]+)\]", text)
    if m:
        coords = re.findall(r"\(([^)]+)\)", m.group(1))
        if coords:
            ground = [tuple(float(x) for x in c.split(",")) for c in coords]

    # Find buildings
    for m in re.finditer(
        r'def Xform "building_\d+" \(([^)]+)\) \{([^}]+)\}', text, re.DOTALL
    ):
        payload_match = re.search(r"@([^@]+)@", m.group(1))
        trans_match = re.search(
            r"xformOp:translate = \(([^)]+)\)", m.group(2)
        )
        rot_match = re.search(
            r"xformOp:rotateXYZ = \(([^)]+)\)", m.group(2)
        )
        if payload_match and trans_match:
            glb_rel = payload_match.group(1)
            glb_path = os.path.join(base_dir, glb_rel)
            tx, ty, tz = (float(x) for x in trans_match.group(1).split(","))
            rot_y = float(rot_match.group(1).split(",")[1]) if rot_match else 0
            buildings.append(
                {
                    "glb": glb_path,
                    "translate": (tx, ty, tz),
                    "rotate_y": rot_y,
                }
            )
    return ground, buildings


def load_glb(path):
    """Load vertex data from a binary GLB file."""
    with open(path, "rb") as f:
        data = f.read()

    # Parse header
    magic = struct.unpack_from("<I", data, 0)[0]
    version = struct.unpack_from("<I", data, 4)[0]
    length = struct.unpack_from("<I", data, 8)[0]

    if magic != 0x46546C67:
        raise ValueError(f"Not a GLB file: {path}")

    pos = 12
    json_str = None
    bin_data = None
    while pos < length:
        chunk_len = struct.unpack_from("<I", data, pos)[0]
        chunk_type = struct.unpack_from("<I", data, pos + 4)[0]
        chunk_start = pos + 8
        if chunk_type == 0x4E4F534A:  # JSON
            json_str = data[chunk_start : chunk_start + chunk_len].decode("utf-8")
        elif chunk_type == 0x004E4942:  # BIN
            bin_data = data[chunk_start : chunk_start + chunk_len]
        pos += 8 + chunk_len

    if not json_str or bin_data is None:
        raise ValueError(f"Invalid GLB: {path}")

    doc = json.loads(json_str)

    # Extract vertex data
    accessors = doc.get("accessors", [])
    bvs = doc.get("bufferViews", [])

    def get_accessor_data(acc_idx, component_type, count_per_vertex, fmt):
        acc = accessors[acc_idx]
        bv = bvs[acc["bufferView"]]
        offset = bv.get("byteOffset", 0)
        stride = bv.get("byteStride", 0)
        count = acc["count"]
        elem_size = struct.calcsize(fmt)
        result = []
        for i in range(count):
            off = offset + i * (stride if stride else elem_size)
            vals = struct.unpack_from(fmt, bin_data, off)
            result.append(vals[:count_per_vertex])
        return result, count

    # Find position accessor (usually index 0)
    mesh = doc.get("meshes", [{}])[0]
    prim = mesh.get("primitives", [{}])[0]
    attrs = prim.get("attributes", {})

    pos_idx = attrs.get("POSITION")
    normal_idx = attrs.get("NORMAL")
    uv_idx = attrs.get("TEXCOORD_0")
    idx_idx = prim.get("indices")

    verts = []
    if pos_idx is not None:
        verts, vc = get_accessor_data(pos_idx, 5126, 3, "<fff")
    normals = []
    if normal_idx is not None:
        normals, _ = get_accessor_data(normal_idx, 5126, 3, "<fff")
    uvs = []
    if uv_idx is not None:
        uvs, _ = get_accessor_data(uv_idx, 5126, 2, "<ff")

    indices = []
    if idx_idx is not None:
        indices, _ = get_accessor_data(idx_idx, 5125, 1, "<I")

    # Get material
    mat_idx = prim.get("material", 0)
    materials = doc.get("materials", [])
    color = [0.7, 0.7, 0.7]
    if mat_idx < len(materials):
        pbr = materials[mat_idx].get("pbrMetallicRoughness", {})
        bc = pbr.get("baseColorFactor", [0.7, 0.7, 0.7, 1.0])
        color = bc[:3]

    return {
        "vertices": verts,
        "normals": normals if normals else [[0, 1, 0]] * len(verts),
        "uvs": uvs if uvs else [[0, 0]] * len(verts),
        "indices": [i for tri in indices for i in tri] if indices else [],
        "color": color,
    }


class CityViewer:
    def __init__(self, usda_path):
        self.win = window.Window(
            fullscreen=False, width=1280, height=720, caption="City Viewer"
        )
        self.win.set_exclusive_mouse(True)

        ground, buildings = read_usda(usda_path)
        self.meshes = []
        self.rot_x = 30
        self.rot_y = 0
        self.dist = 150
        self.mouse_captured = True

        # Load ground mesh
        if ground:
            self.meshes.append(
                {
                    "vertices": ground,
                    "normals": [(0, 1, 0)] * len(ground),
                    "indices": [0, 1, 2, 0, 2, 3],
                    "color": (0.3, 0.35, 0.25),
                }
            )

        # Load building meshes
        for b in buildings:
            if not os.path.exists(b["glb"]):
                continue
            try:
                mesh = load_glb(b["glb"])
                tx, ty, tz = b["translate"]
                ry = np.radians(b["rotate_y"])
                mesh["translate"] = (tx, ty, tz)
                mesh["rotate_y"] = ry
                self.meshes.append(mesh)
            except Exception:
                pass

        print(f"Loaded {len(self.meshes)} meshes")
        self._setup_gl()

    def _setup_gl(self):
        glClearColor(0.6, 0.65, 0.7, 1.0)
        glEnable(GL_DEPTH_TEST)

        # Create shader program
        self.program = glCreateProgram()
        vs = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vs, VERTEX_SHADER)
        glCompileShader(vs)
        fs = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fs, FRAGMENT_SHADER)
        glCompileShader(fs)
        glAttachShader(self.program, vs)
        glAttachShader(self.program, fs)
        glLinkProgram(self.program)

        self.u_modelview = glGetUniformLocation(self.program, "modelview")
        self.u_projection = glGetUniformLocation(self.program, "projection")
        self.u_normal_matrix = glGetUniformLocation(self.program, "normal_matrix")
        self.u_light_dir = glGetUniformLocation(self.program, "light_dir")
        self.u_base_color = glGetUniformLocation(self.program, "base_color")

        # Build VBOs
        self.vbos = []
        for mesh in self.meshes:
            verts = mesh["vertices"]
            normals = mesh.get("normals", [[0, 1, 0]] * len(verts))
            uvs = mesh.get("uvs", [[0, 0]] * len(verts))
            indices = mesh.get("indices", [])

            vbo_data = []
            for i in range(len(verts)):
                vbo_data.extend(verts[i])
                vbo_data.extend(normals[i] if i < len(normals) else [0, 1, 0])
                vbo_data.extend(uvs[i] if i < len(uvs) else [0, 0])

            vbo = glGenBuffers(3)
            # Vertex VBO (interleaved pos+normal+uv)
            glBindBuffer(GL_ARRAY_BUFFER, vbo[0])
            glBufferData(GL_ARRAY_BUFFER, (GLfloat * len(vbo_data))(*vbo_data), GL_STATIC_DRAW)
            # Index VBO
            if indices:
                glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, vbo[1])
                glBufferData(GL_ELEMENT_ARRAY_BUFFER, (GLuint * len(indices))(*indices), GL_STATIC_DRAW)

            self.vbos.append({
                "vbo": vbo,
                "count": len(verts),
                "index_count": len(indices),
                "color": mesh.get("color", (0.7, 0.7, 0.7)),
                "translate": mesh.get("translate", (0, 0, 0)),
                "rotate_y": mesh.get("rotate_y", 0),
                "stride": 8 * 4,  # 8 floats per vertex (3 pos + 3 normal + 2 uv)
            })

    def on_mouse_motion(self, x, y, dx, dy):
        if self.mouse_captured:
            self.rot_y += dx * 0.3
            self.rot_x += dy * 0.3
            self.rot_x = max(-89, min(89, self.rot_x))

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.on_mouse_motion(x, y, dx, dy)

    def on_key_press(self, symbol, modifiers):
        if symbol == window.key.ESCAPE:
            self.win.close()

    def update(self, dt):
        pass

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)

    def run(self):
        clock.schedule(self.update)

        while not self.win.has_exit:
            self.win.dispatch_events()
            dt = clock.tick()
            self.draw()
            self.win.flip()

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.program)

        w, h = self.win.width, self.win.height
        aspect = w / h
        proj = np.array([
            [1 / (aspect * np.tan(np.radians(30))), 0, 0, 0],
            [0, 1 / np.tan(np.radians(30)), 0, 0],
            [0, 0, -(1000 + 1) / (1000 - 1), -2 * 1000 * 1 / (1000 - 1)],
            [0, 0, -1, 0],
        ], dtype=np.float32)
        glUniformMatrix4fv(self.u_projection, 1, GL_TRUE, proj)

        light = np.array([0.5, 1.0, 0.3], dtype=np.float32)
        light = light / np.linalg.norm(light)
        glUniform3fv(self.u_light_dir, 1, light)

        for v in self.vbos:
            # Model matrix: translate then rotate Y
            tx, ty, tz = v["translate"]
            ry = v["rotate_y"]
            cos_y, sin_y = np.cos(ry), np.sin(ry)

            model = np.eye(4, dtype=np.float32)
            model[0:3, 3] = [tx, ty, tz]
            rot = np.eye(4, dtype=np.float32)
            rot[0, 0] = cos_y
            rot[0, 2] = sin_y
            rot[2, 0] = -sin_y
            rot[2, 2] = cos_y
            model = model @ rot

            # View matrix: orbit
            view = np.eye(4, dtype=np.float32)
            rx, ry_angle = np.radians(self.rot_x), np.radians(self.rot_y)
            view[0:3, 3] = [0, 0, -self.dist]
            rot_x_mat = np.eye(4, dtype=np.float32)
            rot_x_mat[1, 1] = np.cos(rx)
            rot_x_mat[1, 2] = -np.sin(rx)
            rot_x_mat[2, 1] = np.sin(rx)
            rot_x_mat[2, 2] = np.cos(rx)
            view = view @ rot_x_mat
            rot_y_mat = np.eye(4, dtype=np.float32)
            rot_y_mat[0, 0] = np.cos(ry_angle)
            rot_y_mat[0, 2] = np.sin(ry_angle)
            rot_y_mat[2, 0] = -np.sin(ry_angle)
            rot_y_mat[2, 2] = np.cos(ry_angle)
            view = view @ rot_y_mat

            mv = view @ model
            glUniformMatrix4fv(self.u_modelview, 1, GL_TRUE, mv)

            nm = np.linalg.inv(mv[:3, :3]).T
            glUniformMatrix3fv(self.u_normal_matrix, 1, GL_TRUE, nm)

            glUniform3fv(self.u_base_color, 1, np.array(v["color"], dtype=np.float32))

            glBindBuffer(GL_ARRAY_BUFFER, v["vbo"][0])
            stride = v["stride"]
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
            glEnableVertexAttribArray(2)
            glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))

            if v["index_count"] > 0:
                glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, v["vbo"][1])
                glDrawElements(GL_TRIANGLES, v["index_count"], GL_UNSIGNED_INT, None)
            else:
                glDrawArrays(GL_TRIANGLES, 0, v["count"])

        glUseProgram(0)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/city_gen/city.usda"
    viewer = CityViewer(path)
    viewer.run()