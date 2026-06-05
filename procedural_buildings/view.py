"""OBJ viewer with directional lighting, orbit controls, and wireframe toggle.

Usage:
    python -m procedural_buildings.view <file.obj>
"""

import math
import sys

import numpy as np
import pyglet
import pyglet.gl as gl
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.window import key, mouse

VERTEX_SOURCE = """#version 150 core
    in vec3 position;
    in vec3 normal;
    in vec3 colour;
    uniform mat4 modelview;
    uniform mat4 projection;
    uniform mat3 normal_matrix;
    out vec3 v_normal;
    out vec3 v_colour;
    void main() {
        v_normal = normalize(normal_matrix * normal);
        v_colour = colour;
        gl_Position = projection * modelview * vec4(position, 1.0);
    }
"""

FRAGMENT_SOURCE = """#version 150 core
    in vec3 v_normal;
    in vec3 v_colour;
    out vec4 frag_colour;
    uniform vec3 light_dir;
    void main() {
        vec3 n = normalize(v_normal);
        vec3 l = normalize(light_dir);
        float diff = max(dot(n, l), 0.0);
        float ambient = 0.35;
        float intensity = ambient + (1.0 - ambient) * diff;
        frag_colour = vec4(v_colour * intensity, 1.0);
    }
"""


def _parse_obj(path):
    """Parse OBJ with # colour(r,g,b) annotations.

    Returns (positions, normals, colours) as flat float32 arrays
    where each row of 3 floats is one vertex attribute.
    Normals are computed as vertex-averaged face normals (smooth shading).
    """
    verts = []
    faces = []
    face_colours = []
    current_colour = None

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if not parts:
                continue
            if parts[0] == "v" and len(parts) >= 4:
                verts.append([float(x) for x in parts[1:4]])
            elif parts[0] == "o":
                colour_marker = "# colour("
                if "#" in line and colour_marker in line:
                    colour_part = line.split(colour_marker, 1)[1].rstrip(")")
                    current_colour = [float(x) for x in colour_part.split(",")]
                else:
                    current_colour = None
            elif parts[0] == "f":
                indices = []
                for p in parts[1:]:
                    v_idx = int(p.split("/")[0]) - 1
                    indices.append(v_idx)
                for i in range(1, len(indices) - 1):
                    faces.append((indices[0], indices[i], indices[i + 1]))
                    face_colours.append(current_colour)

    if not faces:
        return np.array([], dtype=np.float32), np.array([], dtype=np.float32), np.array([], dtype=np.float32)

    verts_arr = np.array(verts, dtype=np.float32)
    n_verts = len(verts_arr)

    norm_accum = np.zeros((n_verts, 3), dtype=np.float32)
    for tri in faces:
        v0 = verts_arr[tri[0]]
        v1 = verts_arr[tri[1]]
        v2 = verts_arr[tri[2]]
        n = np.cross(v1 - v0, v2 - v0)
        norm_len = np.linalg.norm(n)
        if norm_len > 0:
            n /= norm_len
        for idx in tri:
            norm_accum[idx] += n

    for i in range(n_verts):
        norm_len = np.linalg.norm(norm_accum[i])
        if norm_len > 0:
            norm_accum[i] /= norm_len

    positions = []
    normals = []
    colours = []
    for tri, col in zip(faces, face_colours, strict=True):
        for idx in tri:
            positions.append(verts_arr[idx])
            normals.append(norm_accum[idx])
            if col is not None:
                colours.append(col)
            else:
                colours.append([0.8, 0.8, 0.8])

    return (
        np.array(positions, dtype=np.float32),
        np.array(normals, dtype=np.float32),
        np.array(colours, dtype=np.float32),
    )


class Viewer(pyglet.window.Window):
    def __init__(self, obj_path):
        display = pyglet.display.get_display()
        screen = display.get_default_screen()
        super().__init__(
            width=1024, height=768, caption="Building Viewer", resizable=True, visible=False, screen=screen
        )

        positions, normals, colours = _parse_obj(obj_path)
        self.n_vertices = len(positions)
        if self.n_vertices == 0:
            print(f"No geometry found in {obj_path}")
            sys.exit(1)

        vert_shader = Shader(VERTEX_SOURCE, "vertex")
        frag_shader = Shader(FRAGMENT_SOURCE, "fragment")
        self.program = ShaderProgram(vert_shader, frag_shader)

        data = np.hstack([positions, normals, colours]).flatten().astype(np.float32)
        stride = 9 * 4
        self.vlist = self.program.vertex_list(
            self.n_vertices,
            gl.GL_TRIANGLES,
            buffer=("vbo", data.tobytes()),
            position=("f", 3, 0, stride),
            normal=("f", 3, 12, stride),
            colour=("f", 3, 24, stride),
        )

        self.azimuth = 0.0
        self.elevation = 25.0
        self.distance = 50.0
        self.wireframe = False
        self._drag_start = None
        self._prev_azimuth = 0.0
        self._prev_elevation = 25.0

        centre = positions.mean(axis=0)
        max_extent = float(np.max(np.abs(positions - centre)))
        self.distance = max_extent * 3.5
        if self.distance < 1.0:
            self.distance = 10.0

        self._modelview = np.eye(4, dtype=np.float32)
        self._projection = np.eye(4, dtype=np.float32)
        self._update_view()

        self.set_visible(True)

    def _update_view(self):
        az = math.radians(self.azimuth)
        el = math.radians(self.elevation)
        cx = self.distance * math.cos(el) * math.sin(az)
        cy = self.distance * math.sin(el)
        cz = self.distance * math.cos(el) * math.cos(az)

        look = np.array([-cx, -cy, -cz], dtype=np.float32)
        look_len = np.linalg.norm(look)
        if look_len > 0:
            look /= look_len
        up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        right = np.cross(look, up)
        right_len = np.linalg.norm(right)
        if right_len > 0:
            right /= right_len
        up = np.cross(right, look)

        self._modelview = np.array(
            [
                [right[0], right[1], right[2], 0.0],
                [up[0], up[1], up[2], 0.0],
                [look[0], look[1], look[2], 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=np.float32,
        )

        translate = np.eye(4, dtype=np.float32)
        translate[3, :3] = [-cx, -cy, -cz]
        self._modelview = self._modelview @ translate

    def _update_projection(self):
        aspect = self.width / max(self.height, 1)
        fov = 45.0
        f = 1.0 / math.tan(math.radians(fov) / 2.0)
        n = 0.1
        fa = 200.0
        self._projection = np.array(
            [
                [f / aspect, 0, 0, 0],
                [0, f, 0, 0],
                [0, 0, (fa + n) / (n - fa), 2 * fa * n / (n - fa)],
                [0, 0, -1, 0],
            ],
            dtype=np.float32,
        )

    def on_draw(self):
        self.clear()
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)
        gl.glCullFace(gl.GL_BACK)

        if self.wireframe:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        else:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

        self.program.use()
        self.program.set_uniform("modelview", self._modelview.flatten())
        self.program.set_uniform("projection", self._projection.flatten())
        nm = np.linalg.inv(self._modelview[:3, :3]).T.flatten()
        self.program.set_uniform("normal_matrix", nm)
        self.program.set_uniform("light_dir", [0.577, 0.577, 0.577])
        self.vlist.draw(gl.GL_TRIANGLES)

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self._update_projection()

    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            self._drag_start = (x, y)
            self._prev_azimuth = self.azimuth
            self._prev_elevation = self.elevation

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & mouse.LEFT and self._drag_start:
            self.azimuth = self._prev_azimuth + (x - self._drag_start[0]) * 0.3
            self.elevation = self._prev_elevation + (y - self._drag_start[1]) * 0.3
            self.elevation = max(-89.0, min(89.0, self.elevation))
            self._update_view()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.distance *= 1.0 - scroll_y * 0.08
        self.distance = max(0.5, self.distance)
        self._update_view()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.W:
            self.wireframe = not self.wireframe
        elif symbol == key.ESCAPE:
            pyglet.app.exit()

    def on_close(self):
        pyglet.app.exit()


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m procedural_buildings.view <file.obj>")
        sys.exit(1)

    Viewer(sys.argv[1])
    pyglet.app.run()


if __name__ == "__main__":
    main()
