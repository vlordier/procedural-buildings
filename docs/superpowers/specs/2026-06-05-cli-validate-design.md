# 1.3 — `--validate` Flag for Grammar Linting

## Goal
Add a `--validate` flag to the CLI that parses a grammar, runs the op graph
through `simplify`, and exits 0 (or non-zero on failure) without writing any
`.obj` file. Lets grammar authors catch syntax and structural errors in
under a second.

## Approach
Add `--validate` to the CLI. When set, the run skips `grammarToManyObjs` and
calls a new `Processor.validateGrammar(inFile, startRule)` method that
parses and simplifies, returning a non-zero exit code on any error.

## File: `procedural_buildings/Processor.py`

Add a method:
```python
def validateGrammar(self, inFile, startRule="plot"):
    """Parse and simplify a grammar, raising on any error.
    Returns the simplified op graph root on success."""
    with open(inFile) as f:
        grammarText = f.read()
    # Mirror what grammarToManyObjs does, up to and including simplify
    self.grammarText = grammarText
    self.parse(grammarText)
    self.makeOps()
    self.process()
    self.simplify()
    return self
```

The exact internal API will follow the existing `grammarToManyObjs`
implementation. This may need an additional refactor inside Processor to
expose the parse→ops→process→simplify pipeline. Worst case, copy the
relevant lines and call them.

## File: `procedural_buildings/__main__.py`

```python
validate = False
# In opts:
elif opt in ("--validate",):
    validate = True
# Add "validate" to long opts and "validate" handling.

# After gin parsing, replace the rev/grammar branch:
if validate:
    try:
        p = Processor()
        p.validateGrammar(inFile, startRule)
        log.info(f"Validation passed: {inFile}")
        sys.exit(0)
    except Exception as e:
        log.error(f"Validation failed: {e}")
        sys.exit(1)
```

Usage string addition:
```
" [--validate]"
```

## Test
```python
# tests/test_cli_validate.py
import subprocess

def test_validate_passes_on_valid_grammar():
    result = subprocess.run(
        ["python", "-m", "procedural_buildings",
         "--validate", "-i", "grammars/orthodox_church"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0

def test_validate_fails_on_nonexistent_grammar():
    result = subprocess.run(
        ["python", "-m", "procedural_buildings",
         "--validate", "-i", "grammars/this_does_not_exist"],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
```

We can add a "fails on syntactically broken grammar" test by writing a tmp
file with `plot --> R(z, pi/6){I(rect)}` (which is broken because the lexer
chokes on `/`) and asserting non-zero.

## Acceptance
- `python -m procedural_buildings --validate -i grammars/orthodox_church`
  exits 0 in < 1s, writes nothing.
- A broken grammar exits non-zero with a clear error message.

## Out of scope
- Detailed validation (e.g., "this rule is unreachable") — that's a future
  item. For now, "validates" means "parses + simplifies without raising".
