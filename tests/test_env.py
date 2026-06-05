"""Tests that width/depth/height propagate correctly through operations."""

import numpy as np

from procedural_buildings._names import Face
from procedural_buildings.ContextObj import ContextOBJ
from procedural_buildings.Ops import OpColour, OpComp, OpResizeScope, OpSplit, scope_env
from procedural_buildings.parsing.Rule import Size
from procedural_buildings.Scope import Scope


def test_scope_env_includes_dimensions():
    scope = Scope(np.array([0, 0, 0]), np.eye(3), np.array([5.0, 10.0, 15.0]))
    env = scope_env({}, scope)
    assert env["width"] == 5.0
    assert env["depth"] == 10.0
    assert env["height"] == 15.0


def test_scope_env_preserves_existing():
    scope = Scope(np.array([0, 0, 0]), np.eye(3), np.array([5.0, 10.0, 15.0]))
    env = scope_env({"foo": "bar"}, scope)
    assert env["foo"] == "bar"
    assert env["width"] == 5.0


def test_scope_env_does_not_mutate_original():
    original = {"a": 1}
    scope = Scope(np.array([0, 0, 0]), np.eye(3), np.array([5.0, 10.0, 15.0]))
    env = scope_env(original, scope)
    env["a"] = 2
    assert original["a"] == 1


def test_scope_env_neighbors():
    scope = Scope(np.array([0, 0, 0]), np.eye(3), np.array([5.0, 10.0, 15.0]))
    left = Scope(np.array([-5, 0, 0]), np.eye(3), np.array([5.0, 10.0, 15.0]))
    right = Scope(np.array([5, 0, 0]), np.eye(3), np.array([6.0, 12.0, 18.0]))
    scope.neighbors["left_width"] = left.size
    scope.neighbors["right_width"] = right.size
    env = scope_env({}, scope)
    assert env["left_width"] == 5.0
    assert env["left_depth"] == 10.0
    assert env["left_height"] == 15.0
    assert env["right_width"] == 6.0
    assert env["right_depth"] == 12.0
    assert env["right_height"] == 18.0


def test_split_propagates_child_dimensions():
    context = ContextOBJ()
    scope = Scope(np.array([0, 0, 0]), np.eye(3), np.array([10.0, 10.0, 10.0]))
    captured = {}

    class CaptureOp:
        def run(self, context, scope, env):
            captured["width"] = env.get("width")
            captured["depth"] = env.get("depth")
            captured["height"] = env.get("height")

    split = OpSplit(0, perChildArgs=(Size(5.0, False), Size(5.0, False)), childOps=[CaptureOp(), CaptureOp()])
    split.run(context, scope, {})
    assert captured["width"] == 5.0
    assert captured["depth"] == 10.0
    assert captured["height"] == 10.0


def test_split_neighbors_propagate():
    context = ContextOBJ()
    scope = Scope(np.array([0, 0, 0]), np.eye(3), np.array([10.0, 10.0, 10.0]))
    captured = []

    class CaptureOp:
        def run(self, context, scope, env):
            captured.append({
                "left_w": env.get("left_width"),
                "right_w": env.get("right_width"),
            })

    split = OpSplit(
        0,
        perChildArgs=(Size(3.0, False), Size(4.0, False), Size(3.0, False)),
        childOps=[CaptureOp(), CaptureOp(), CaptureOp()],
    )
    split.run(context, scope, {})
    assert len(captured) == 3
    assert captured[0].get("left_w") is None
    assert captured[0].get("right_w") == 4.0
    assert captured[1].get("left_w") == 3.0
    assert captured[1].get("right_w") == 3.0
    assert captured[2].get("left_w") == 4.0
    assert captured[2].get("right_w") is None


def test_resize_updates_dimensions():
    context = ContextOBJ()
    scope = Scope(np.array([0, 0, 0]), np.eye(3), np.array([10.0, 10.0, 10.0]))
    captured = {}

    class CaptureOp:
        def run(self, context, scope, env):
            captured["width"] = env.get("width")

    resize = OpResizeScope(Size(20.0, False), Size(20.0, False), Size(20.0, False), childOps=[CaptureOp()])
    resize.run(context, scope, {})
    assert captured["width"] == 20.0


def test_colour_propagates_dimensions():
    context = ContextOBJ()
    scope = Scope(np.array([0, 0, 0]), np.eye(3), np.array([7.0, 14.0, 21.0]))
    captured = {}

    class CaptureOp:
        def run(self, context, scope, env):
            captured["width"] = env.get("width")
            captured["depth"] = env.get("depth")
            captured["height"] = env.get("height")

    colour = OpColour(0.5, 0.5, 0.5, childOps=[CaptureOp()])
    colour.run(context, scope, {})
    assert captured["width"] == 7.0
    assert captured["depth"] == 14.0
    assert captured["height"] == 21.0


def test_comp_propagates_face_dimensions():
    context = ContextOBJ()
    scope = Scope(np.array([0, 0, 0]), np.eye(3), np.array([10.0, 20.0, 30.0]))
    captured = {}

    class CaptureOp:
        def run(self, context, scope, env):
            captured["width"] = env.get("width")
            captured["depth"] = env.get("depth")
            captured["height"] = env.get("height")

    comp = OpComp(perChildArgs=(Face.FRONT,), childOps=[CaptureOp()])
    comp.run(context, scope, {})
    assert captured["width"] == 10.0
    assert captured["depth"] == 0.0
    assert captured["height"] == 30.0


def test_nested_dimensions():
    """Split then resize: child should get the resized dimensions."""
    context = ContextOBJ()
    scope = Scope(np.array([0, 0, 0]), np.eye(3), np.array([10.0, 10.0, 10.0]))
    captured = []

    class CaptureOp:
        def run(self, context, scope, env):
            captured.append(env.get("width"))

    inner = OpResizeScope(Size(5.0, False), Size(5.0, False), Size(5.0, False), childOps=[CaptureOp()])
    outer = OpSplit(0, perChildArgs=(Size(3.0, False), Size(7.0, False)), childOps=[CaptureOp(), inner])
    outer.run(context, scope, {})
    assert captured[0] == 3.0
    assert captured[1] == 5.0
