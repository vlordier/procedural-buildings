# B2 — Fix Lexer.error Corruption

## Goal
`Lexer.error` at `Lexer.py:125-127` warns and advances one character.
A single bad character in a 200-line grammar file yields a cascade of
spurious tokenisation errors. Collect errors and raise at end instead.

## Change
```python
def error(self, t):
    self.errors.append(f"Illegal character '{t.value[0]}' at line {self.lineno}")
    self.index += 1
```

Add `self.errors = []` in `__init__`, then in `GrammarParser.parse` or
in `Lexer.tokenize`, check `self.errors` after tokenisation and raise
if non-empty.

## Testing
Add a test: `test_lexer_bad_char_raises` that tokenises `"plot --> R(z, pi/6){I(rect)}"` (contains `/`) and asserts it raises.

```python
def test_lexer_bad_char_raises(self):
    lexer = Lexer()
    with pytest.raises(Exception, match="Illegal character"):
        list(lexer.tokenize("plot --> R(z, pi/6){I(rect)}"))
```