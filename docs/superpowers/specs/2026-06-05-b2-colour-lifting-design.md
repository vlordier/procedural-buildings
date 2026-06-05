# B6 — Colour Lifting in Reverse Path

## Goal
Currently the reverse path wraps each box individually in `OpColour`:
```
split(x){~1 : colour(r,g,b){I(rect)} | ~1 : colour(r,g,b){I(rect2)}}
```
Colour lifting merges adjacent boxes with the same colour into a single
`OpColour` wrapper around a `OpSplit`:
```
colour(r,g,b){split(x){~1 : I(rect) | ~1 : I(rect2)}}
```
This produces cleaner grammar output and smaller grammar text.

## Approach
Post-processing pass in `BoxSplitter.py` (or a new function) that walks
the op tree after `boxesToOp` and lifts colour wrappers up.

After `boxesToOp(boxes, container)` returns an op tree, run:
```python
def lift_colour(op):
    """Walk op tree, lift OpColour wrappers above OpSplit when adjacent
    children share the same colour."""
    if not hasattr(op, "childOps") or not op.childOps:
        return op
    op.childOps = [lift_colour(c) for c in op.childOps]

    if isinstance(op, OpSplit):
        # Group consecutive children with identical OpColour wrappers
        new_children = []
        i = 0
        while i < len(op.childOps):
            child = op.childOps[i]
            if isinstance(child, OpColour):
                # Look ahead for adjacent OpColour with same colour
                group = [child.childOps[0]]
                j = i + 1
                while (j < len(op.childOps) and
                       isinstance(op.childOps[j], OpColour) and
                       op.childOps[j].args == child.args):
                    group.append(op.childOps[j].childOps[0])
                    j += 1
                if len(group) > 1:
                    # Create a sub-split for the group
                    sub_sizes = [op.perChildArgs[k] for k in range(i, j)]
                    sub_split = OpSplit(op.axis, perChildArgs=tuple(sub_sizes),
                                        childOps=group)
                    new_children.append(OpColour(child.args, childOps=sub_split))
                    i = j
                    continue
            new_children.append(child)
            i += 1
        op.childOps = new_children
    return op
```

Call `lift_colour` at the end of `boxesToOp()`.

## Testing
Update `tests/test_colour.py` to assert that the lifted tree has
`OpColour` wrapping `OpSplit` instead of individual `OpColour` per leaf: