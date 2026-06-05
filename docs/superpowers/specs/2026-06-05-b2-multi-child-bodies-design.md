# B4 — Multi-Child Rule Bodies

## Goal
Allow rules to emit multiple top-level ops directly:
`rule --> split(x){...} | split(y){...} | I(rect)`
instead of requiring a wrapper rule.

## Approach
Currently the parser produces a single `Right` with one op per rule.
Change the grammar to allow `right_expr \| right_expr` as an
`OpChooseRuleWithPriority`.

In `Parser.py`, add a production:
```python
@_("right_expr PIPE right_expr")
def right_expr(self, p):
    return Right(p.right_expr0, priority=None)
    # Priority tracking will merge them
```

Actually, the existing multi-rule system uses separate rule definitions
with the same label:
```
rule --> A : 0.5
rule --> B : 0.5
```

Multi-child bodies are syntactic sugar for the same thing:
```
rule --> A | B
```

The change is in the parser: when a `|` is encountered in a rule body,
split into multiple `Right` objects with the same `Left`, creating
separate rule entries. The Checker already handles multiple rules with
the same label (creates `OpChooseRuleWithPriority`).

## Parser change
In the rule production, when the body contains `|`, produce multiple
`(Left, Right)` pairs instead of one. The Checker merges them.

## Example
```
house --> I(rect) | colour(1,0,0){I(rect)}
```
is equivalent to:
```
house --> I(rect) : 1
house --> colour(1,0,0){I(rect)} : 1
```

## Testing
Add `grammars/op_tests/multi_body`:
```grammar
plot --> I(rect) | I(triangle)
```
And a test in `tests/test_parser.py` or `tests/test_op_grammars.py`.