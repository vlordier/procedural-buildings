import numpy as np

from procedural_buildings.ContextObj import ContextOBJ
from procedural_buildings.ObjReader import objToOpGraph
from procedural_buildings.Ops import OpColour, OpPrimitive
from procedural_buildings.Scope import Scope


def _find_op_colour(op):
    if isinstance(op, OpColour):
        return True
    if hasattr(op, "childOps") and op.childOps:
        return any(_find_op_colour(c) for c in op.childOps)
    return False


def _extract_colour(op):
    if isinstance(op, OpColour):
        col = op.args.evaluate({})[0]
        if col is not None:
            return col
    if hasattr(op, "childOps") and op.childOps:
        for c in op.childOps:
            result = _extract_colour(c)
            if result:
                return result
    return None


def test_colour_written_and_read_back(tmp_path):
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([8, 8, 12]))
    ctx = ContextOBJ()
    ctx.colour((0.5, 0.3, 0.2), scope)
    op = OpPrimitive("rect")
    op.run(ctx, scope, {"width": 8, "depth": 8, "height": 12})
    obj_path = str(tmp_path / "test.obj")
    ctx.writeToFile(obj_path)

    op_graph = objToOpGraph(str(obj_path))
    assert op_graph is not None
    assert _find_op_colour(op_graph), "No OpColour found"


def test_colour_values_preserved(tmp_path):
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([1, 1, 1]))
    ctx = ContextOBJ()
    ctx.colour((0.95, 0.92, 0.88), scope)
    OpPrimitive("rect").run(ctx, scope, {"width": 1, "depth": 1, "height": 1})
    ctx.writeToFile(str(tmp_path / "test.obj"))

    op_graph = objToOpGraph(str(tmp_path / "test.obj"))
    rgb = _extract_colour(op_graph)
    assert rgb is not None
    assert abs(rgb[0] - 0.95) < 0.01
    assert abs(rgb[1] - 0.92) < 0.01
    assert abs(rgb[2] - 0.88) < 0.01


def test_no_colour_does_not_produce_op_colour(tmp_path):
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([1, 1, 1]))
    ctx = ContextOBJ()
    OpPrimitive("rect").run(ctx, scope, {"width": 1, "depth": 1, "height": 1})
    ctx.writeToFile(str(tmp_path / "test.obj"))

    op_graph = objToOpGraph(str(tmp_path / "test.obj"))
    assert not _find_op_colour(op_graph), "OpColour found when none expected"
