# 2.1 — Parser/Lexer Tests

## Goal
Add unit tests for the parsing subsystem: Lexer, GrammarParser, Checker,
and GrammarVars. Cover tokenisation, comment handling, valid/invalid
grammar parsing, rule definition validation, and expression evaluation.

## Approach
One test file `tests/test_parser.py` with four test classes, one per
subsystem. Tests are white-box — they import and call the parsing classes
directly (not via Processor).

## File: `tests/test_parser.py`

### Test class 1: `TestLexer`

```python
import pytest
from procedural_buildings.parsing.Lexer import Lexer

lexer = Lexer()

def test_lexer_ident():
    tokens = list(lexer.tokenize("plot"))
    assert len(tokens) == 1
    assert tokens[0].type == "IDENT"
    assert tokens[0].value == "plot"

def test_lexer_comment_stripped():
    tokens = list(lexer.tokenize("plot # this is a comment\n--> I(rect)"))
    # "plot" + arrow + I + LPAR + rect + RPAR = 6 tokens
    assert len(tokens) == 6
    assert tokens[0].value == "plot"

def test_lexer_split_keyword():
    tokens = list(lexer.tokenize("split"))
    assert len(tokens) == 1
    assert tokens[0].type == "SPLIT"

def test_lexer_float():
    tokens = list(lexer.tokenize("3.14"))
    assert len(tokens) == 1
    assert tokens[0].type == "FLOAT"
    assert tokens[0].value == pytest.approx(3.14)

def test_lexer_int():
    tokens = list(lexer.tokenize("42"))
    assert len(tokens) == 1
    assert tokens[0].type == "INT"
    assert tokens[0].value == 42

def test_lexer_colour_keywords():
    tokens = list(lexer.tokenize("red green blue"))
    assert len(tokens) == 3
    for t in tokens:
        assert t.type == "IDENT"

def test_lexer_operators():
    text = "+ - * / = : --> ~ ( )"
    tokens = list(lexer.tokenize(text))
    types = ["PLUS", "MINUS", "TIMES", "DIVIDE", "ASSIGN",
             "COLON", "ARROW", "TILDE", "LPAR", "RPAR"]
    assert [t.type for t in tokens] == types

def test_lexer_nested_parens():
    tokens = list(lexer.tokenize("colour(0.5, 0.5, 0.5)"))
    assert tokens[0].type == "IDENT"  # colour
    assert tokens[1].type == "LPAR"
    assert tokens[2].type == "FLOAT"
    assert tokens[3].type == "COMMA"
```

### Test class 2: `TestGrammarParser`

GrammarParser is the sly parser. Tests should verify that valid grammar
texts parse to a rule list, and invalid texts raise appropriate errors.

```python
from procedural_buildings.parsing.GrammarParser import GrammarParser
from procedural_buildings.parsing.GrammarVars import GrammarVars

parser = GrammarParser()

def test_parse_simple_grammar():
    text = "plot --> I(rect)\n"
    vars = GrammarVars()
    rules = parser.parse(text, vars)
    assert len(rules) >= 1

def test_parse_with_variables():
    text = "h = 3\nplot --> S(~1, ~1, h){I(rect)}\n"
    vars = GrammarVars()
    rules = parser.parse(text, vars)
    assert len(rules) >= 1
    assert "h" in vars

def test_parse_conditional_rule():
    text = "wall : pattern == 1 --> colour(1,0,0){I(rect)}\n"
    vars = GrammarVars()
    rules = parser.parse(text, vars)
    assert len(rules) >= 1
```

### Test class 3: `TestChecker`

```python
from procedural_buildings.parsing.Checker import Checker

def test_checker_undefined_rule_raises():
    text = "plot --> I(rect)\nfoo --> bar\n"
    checker = Checker()
    with pytest.raises(Exception):
        checker.check(text)  # bar is not defined
```

### Test class 4: `TestGrammarVars`

```python
def test_grammar_vars_declaration():
    vars = GrammarVars()
    vars["h"] = "3"
    assert vars.evaluate("h") == 3

def test_grammar_vars_expression():
    vars = GrammarVars()
    vars["a"] = "3"
    vars["b"] = "4"
    assert vars.evaluate("a + b") == 7
```

## Testing
```bash
cd /Users/vincent/Work/procedural-buildings
uv run --with sly --with numpy --with sympy --with gin-config pytest tests/test_parser.py -v
```

## Out of scope
- Full coverage of GrammarVars expression evaluation (sympy-backed, trust the library)
- Testing the reverse grammar output format (covered by round-trip tests)
- GrammarParser's handling of broken LALR reductions (pre-existing, not a regression risk)