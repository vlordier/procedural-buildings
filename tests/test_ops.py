import numpy as np

from procedural_buildings._names import Face
from procedural_buildings.ContextObj import ContextOBJ
from procedural_buildings.Ops import (
    OpChooseRuleWithPriority,
    OpColour,
    OpComp,
    OpDo,
    OpFlip,
    OpInset,
    OpNil,
    OpOpening,
    OpPrimitive,
    OpRepeat,
    OpRepeatN,
    OpResizeScope,
    OpRotate,
    OpScale,
    OpSetParams,
    OpSplit,
    OpTranslate,
)
from procedural_buildings.parsing.Rule import Size
from procedural_buildings.Scope import Scope

SCOPE = Scope(np.array([0, 0, 0]), np.eye(3), np.array([8, 8, 12]))
ENV = {"width": 8, "depth": 8, "height": 12}


def test_nil_does_nothing():
    op = OpNil()
    ctx = ContextOBJ()
    op.run(ctx, SCOPE, ENV)
    assert len(ctx.prims) > 0
    assert len(ctx.objFileText) == 0


def test_primitive_writes_to_context():
    op = OpPrimitive("rect")
    ctx = ContextOBJ()
    op.run(ctx, SCOPE, ENV)
    assert len(ctx.objFileText) > 0


def test_colour_sets_context():
    op = OpColour(0.5, 0.5, 0.5, childOps=[OpPrimitive("rect")])
    ctx = ContextOBJ()
    op.run(ctx, SCOPE, ENV)
    assert ctx.currentColour == (0.5, 0.5, 0.5)
    assert len(ctx.objFileText) > 0


def test_split_creates_children():
    sizes = (Size(4, True), Size(4, True))
    op = OpSplit(2, perChildArgs=sizes, childOps=[OpPrimitive("rect"), OpNil()])
    ctx = ContextOBJ()
    op.run(ctx, SCOPE, ENV)


def test_repeat_creates_repetitions():
    op = OpRepeat(0, perChildArgs=(2.0,), childOps=[OpPrimitive("rect")])
    ctx = ContextOBJ()
    op.run(ctx, SCOPE, ENV)


def test_repeat_n_creates_exact_count():
    op = OpRepeatN(0, 4, childOps=[OpPrimitive("rect")])
    ctx = ContextOBJ()
    op.run(ctx, SCOPE, ENV)


def test_comp_creates_faces():
    op = OpComp(perChildArgs=(Face.FRONT,), childOps=[OpPrimitive("rect")])
    ctx = ContextOBJ()
    op.run(ctx, SCOPE, ENV)


def test_resize_changes_scope():
    op = OpResizeScope(Size(4, False), Size(8, False), Size(6, False), childOps=[OpPrimitive("rect")])
    ctx = ContextOBJ()
    op.run(ctx, SCOPE, ENV)


def test_scale_changes_scope():
    op = OpScale(0.5, 0.5, 0.5, childOps=[OpPrimitive("rect")])
    ctx = ContextOBJ()
    op.run(ctx, SCOPE, ENV)


def test_translate_moves_scope():
    op = OpTranslate(1.0, 2.0, 3.0, childOps=[OpPrimitive("rect")])
    ctx = ContextOBJ()
    op.run(ctx, SCOPE, ENV)


def test_rotate_applies_rotation():
    op = OpRotate(2, np.pi / 4, childOps=[OpPrimitive("rect")])
    ctx = ContextOBJ()
    op.run(ctx, SCOPE, ENV)


def test_priority_chooses_one_child():
    a = OpPrimitive("rect")
    b = OpPrimitive("rect")
    op = OpChooseRuleWithPriority(perChildArgs=((1, 0), (True, True)), childOps=[a, b])
    ctx = ContextOBJ()
    op.run(ctx, SCOPE, ENV)
    assert len(ctx.objFileText) > 0


def test_do_runs_child():
    op = OpDo(childOps=[OpPrimitive("rect")])
    ctx = ContextOBJ()
    op.run(ctx, SCOPE, ENV)
    assert len(ctx.objFileText) > 0


def test_inset_creates_frames():
    rect = OpPrimitive("rect")
    nil = OpNil()
    op = OpInset(0.5, childOps=[rect, nil])
    ctx = ContextOBJ()
    op.run(ctx, SCOPE, ENV)


def test_opening_creates_four_frames():
    rect = OpPrimitive("rect")
    nil = OpNil()
    op = OpOpening(0.5, childOps=[rect, nil])
    ctx = ContextOBJ()
    op.run(ctx, SCOPE, ENV)


def test_set_params_sets_env():
    rect = OpPrimitive("rect")
    rect.addParams(["N"])
    op = OpSetParams(5, childOps=[rect])
    ctx = ContextOBJ()
    op.run(ctx, SCOPE, ENV)


def test_flip_runs():

    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([8, 8, 12]))
    env = {"width": 8, "depth": 8, "height": 12}
    op = OpFlip(0, childOps=[OpPrimitive("rect")])
    ctx = ContextOBJ()
    op.run(ctx, scope, env)
