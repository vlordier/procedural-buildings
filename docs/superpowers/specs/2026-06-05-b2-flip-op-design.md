# B3 — flip(axis) Op

## Goal
A shorthand for mirroring geometry: `flip(x)` is equivalent to
`S(width*(-1), depth, height){T(width, 0, 0){...}}` or `R(z, pi)`.

## Implementation
New Op subclass in `Ops.py`. Flip mirrors the scope by rotating 180°
around the given axis (equivalent to `R(axis, pi)`):

```python
class OpFlip(Op):
    opName = OpName.FLIP

    def run(self, context, scope, env):
        scope = scope.rotate(axis, math.pi)
        env = scope_env(env, scope)
        self.childOps[0].run(context, scope, env)
```

Parser rule in `Parser.py`: `FLIP LPAR axis RPAR LCURL op RCURL`
Lexer token: `FLIP`.

## Testing
```python
import math

def test_flip_creates_mirrored_geometry():
    scope = Scope.freshScope(np.array([0, 0, 0]), np.array([8, 8, 12]))
    env = {"width": 8, "depth": 8, "height": 12}
    op = OpFlip(perChildArgs=("x",), childOps=[OpPrimitive("rect")])
    ctx = ContextObj()
    op.run(ctx, scope, env)
```

Also add an op_test grammar at `grammars/op_tests/flip`:
```grammar
plot --> flip(x){I(rect)}
```