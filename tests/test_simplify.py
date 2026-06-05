import pytest

from procedural_buildings.Ops import Args, Op, OpNil, OpPrimitive


class TestArgsCombineArgs:
    def test_int_int(self):
        result = Args(42, ()).combineArgs(42, 42)
        assert result == 42

    def test_float_float(self):
        result = Args(3.14, ()).combineArgs(3.14, 3.14)
        assert result == 3.14

    def test_mismatch(self):
        result = Args(42, ()).combineArgs(42, "hello")
        assert result is None

    def test_list_list(self):
        result = Args([1, 2, 3], ()).combineArgs([1, 2, 3], [1, 2, 3])
        assert result == [1, 2, 3]

    def test_tuple_tuple(self):
        result = Args((1, 2), ()).combineArgs((1, 2), (1, 2))
        assert result == (1, 2)

    def test_string_match(self):
        result = Args("hello", ()).combineArgs("hello", "hello")
        assert result == "hello"

    def test_string_mismatch(self):
        result = Args("hello", ()).combineArgs("hello", "world")
        assert result is None

    def test_mixed_list_tuple(self):
        result = Args([1, 2], ()).combineArgs([1, 2], (1, 2))
        assert result is None


class TestOpSimplify:
    def test_identical_prims(self):
        seen = {}
        a = OpPrimitive("rect")
        b = OpPrimitive("rect")
        result_a = a.simplify(seen)
        result_b = b.simplify(seen)
        assert result_b is result_a

    def test_different_prims(self):
        seen = {}
        a = OpPrimitive("rect")
        b = OpPrimitive("triangle")
        result_a = a.simplify(seen)
        result_b = b.simplify(seen)
        assert result_b is not result_a

    def test_nil_and_nil(self):
        seen = {}
        a = OpNil()
        b = OpNil()
        result_a = a.simplify(seen)
        result_b = b.simplify(seen)
        assert result_b is result_a


class TestOpCombineMany:
    def test_all_identical(self):
        ops = [OpPrimitive("rect"), OpPrimitive("rect"), OpPrimitive("rect")]
        result = Op.combineMany(ops)
        assert result is not None

    def test_all_different(self):
        ops = [OpPrimitive("rect"), OpPrimitive("triangle")]
        result = Op.combineMany(ops)
        assert result is not None

    def test_single_op(self):
        result = Op.combineMany([OpPrimitive("rect")])
        assert result is not None

    def test_empty_list(self):
        result = Op.combineMany([])
        assert isinstance(result, OpNil)