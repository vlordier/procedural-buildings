# How to Add a New Operation

## 1. Add the op class to `Ops.py`

Create a new subclass of `Op`. Follow the pattern of existing ops:

```python
class OpMyNewOp(Op):
    opName = "my_new_op"

    def run(self, context, scope, env):
        # 1. Evaluate args
        # 2. Modify scope if needed
        # 3. Call scope_env(env, scope) for child env
        # 4. Run children
        for child in self.childOps:
            child.run(context, new_scope, scope_env(env, new_scope))
```

## 2. Add a parser rule in `Parser.py`

Add a grammar production for the new op. Follow the pattern of existing
production rules. The parser handles the `OPNAME(...){...}` syntax.

## 3. Add the keyword to `Lexer.py`

If the op name isn't already a token, add it to the lexer's token list.

## 4. Add a test grammar in `grammars/op_tests/`

Create a minimal grammar that exercises the new op:

```grammar
plot --> my_new_op(1, 2, 3){I(rect)}
```

## 5. Wire the test grammar into pytest

Add an entry to `tests/test_op_grammars.py` or verify the auto-discover
picks it up.

## 6. Add a unit test

Add a test to `tests/test_ops.py` following the existing pattern:

```python
def test_my_new_op_runs():
    scope = Scope.freshScope(...)
    env = {"width": 8, "depth": 8, "height": 12}
    op = OpMyNewOp(...)
    ctx = ContextObj()
    op.run(ctx, scope, env)
```

## The scope_env contract

Every operation that modifies the scope MUST call `scope_env(env, scope)`
to inject width/depth/height into the child's environment. This function
is in `Ops.py`:

```python
def scope_env(env, scope):
    new_env = env.copy()
    new_env["width"] = scope.size[0]
    new_env["depth"] = scope.size[1]
    new_env["height"] = scope.size[2]
    return new_env
```

If the op passes its scope to children, it MUST call `scope_env` and pass
the result. This is what makes `width`, `depth`, `height`, and neighbour
info available in grammar conditions.

## 7. Run the full test suite

```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/
```