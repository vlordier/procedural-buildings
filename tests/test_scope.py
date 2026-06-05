import numpy as np
import pytest

from procedural_buildings.parsing.Rule import Size
from procedural_buildings.Scope import Scope

POS = np.array([0.0, 0.0, 0.0])
SIZE = np.array([8.0, 8.0, 12.0])


def test_split_creates_three_children():
    scope = Scope.freshScope(POS, SIZE)
    sizes = (Size(4, True), Size(4, True), Size(4, True))
    children = scope.split(2, sizes)
    assert len(children) == 3
    assert abs(sum(c.size[2] for c in children) - 12.0) < 1e-6


def test_split_with_absolute_sizes():
    scope = Scope.freshScope(POS, SIZE)
    sizes = (Size(4, False), Size(8, False))
    children = scope.split(0, sizes)
    assert len(children) == 2
    assert abs(children[0].size[0] - 4.0) < 1e-6
    assert abs(children[1].size[0] - 8.0) < 1e-6


def test_repeat_creates_children():
    scope = Scope.freshScope(POS, SIZE)
    children = scope.repeat(0, 2.0)
    assert len(children) == 4
    for c in children:
        assert abs(c.size[0] - 2.0) < 1e-6


def test_repeat_n_creates_exact_count():
    scope = Scope.freshScope(POS, SIZE)
    children = scope.repeatN(2, 3)
    assert len(children) == 3


def test_comp_front_face():
    scope = Scope.freshScope(POS, np.array([8, 8, 12]))
    face = scope.comp("front")
    assert face is not None
    assert abs(face.size[0] - 8.0) < 1e-6
    assert abs(face.size[2] - 12.0) < 1e-6


def test_comp_top_face():
    scope = Scope.freshScope(POS, np.array([8, 8, 12]))
    face = scope.comp("top")
    assert face is not None
    assert abs(face.size[0] - 8.0) < 1e-6
    assert abs(face.size[1] - 8.0) < 1e-6


def test_comp_invalid_face():
    scope = Scope.freshScope(POS, SIZE)
    with pytest.raises(RuntimeError, match="Invalid face name"):
        scope.comp("invalid_face")


def test_inset_creates_inner_and_four_frames():
    scope = Scope.freshScope(POS, SIZE)
    outer_boxes, inner_box = scope.inset(1.0)
    assert inner_box is not None
    assert len(outer_boxes) == 4
    assert abs(inner_box.size[0] - 6.0) < 1e-6
    assert abs(inner_box.size[1] - 8.0) < 1e-6


def test_opening_creates_child_and_four_frames():
    scope = Scope.freshScope(POS, SIZE)
    outer, child_scope = scope.opening(1.0)
    assert child_scope is not None
    assert len(outer) == 4
    assert abs(child_scope.size[0] - 8.0) < 1e-6


def test_translate():
    scope = Scope.freshScope(POS, SIZE)
    new_scope = scope.translate(np.array([1.0, 2.0, 3.0]))
    assert np.allclose(new_scope.pos, [1, 2, 3])
    assert np.allclose(new_scope.size, [8, 8, 12])


def test_rotate_z():
    scope = Scope.freshScope(POS, SIZE)
    rotated = scope.rotate(2, np.pi / 2)
    assert rotated is not None


def test_resize():
    scope = Scope.freshScope(POS, SIZE)
    new_sizes = [Size(4, False), Size(8, False), Size(6, False)]
    resized = scope.resize(new_sizes)
    assert np.allclose(resized.size, [4, 8, 6])


def test_scale():
    scope = Scope.freshScope(POS, SIZE)
    scaled = scope.scale(0.5)
    assert np.allclose(scaled.size, [4, 4, 6])


def test_fresh_scope():
    scope = Scope.freshScope(np.array([0.0, 0.0, 0.0]), np.array([1.0, 2.0, 3.0]))
    assert np.allclose(scope.pos, [0, 0, 0])
    assert np.allclose(scope.size, [1, 2, 3])
