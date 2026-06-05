# B5 — Env-Conditional Rules

## Goal
Allow conditions based on env variables (not just rule parameters):
`rule : width > 5 --> ...` instead of requiring `left_width` hacks.

## Approach
Currently conditions in the Checker compare rule parameter values. Add
a secondary condition system: if a condition contains only env variable
names (width, depth, height, left_width, etc.), evaluate it against the
env dict at rule-dispatch time.

## Changes

**`Ops.py` — `OpChooseRuleWithPriority.run()`:**
Before choosing a child, evaluate the conditions against the current env.
Currently conditions are evaluated as expressions. Add env variables to
the symbol table before evaluating:

```python
def chooseChild(self, env):
    priorities, conditions = self.args.evaluate(env)[0]
    # Evaluate conditions with env vars available
    filtered = []
    for i, p in enumerate(priorities):
        if conditions[i] is None or evaluate_condition(conditions[i], env):
            filtered.append((i, p))
```

Where `evaluate_condition` adds env vars to the sympy symbol table.

**No parser changes** — conditions already support arbitrary expressions.
The grammar syntax `rule : N > 3 --> ...` already works for param
conditions. Env conditions use the same syntax but resolve env variables
instead of rule parameters.

## Example
```
facade : width > 10 --> split(x){~1 : I(rect) | ~2 : I(rect)}
facade : width <= 10 --> I(rect)
```

## Testing
Add a test grammar `grammars/op_tests/env_conditions`:
```grammar
plot --> S(~1, ~1, 12){checkWidth}
checkWidth : width > 10 --> split(x){~1 : colour(1,0,0){I(rect)} | ~1 : colour(0,1,0){I(rect)}}
checkWidth : width <= 10 --> I(rect)
```