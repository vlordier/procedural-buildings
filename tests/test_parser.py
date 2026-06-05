"""Tests for Lexer, GrammarParser, Checker, and GrammarVars."""

import pytest

from procedural_buildings.Ops import OpPrimitive
from procedural_buildings.parsing.Checker import Checker
from procedural_buildings.parsing.GrammarParser import GrammarParser
from procedural_buildings.parsing.GrammarVars import get_grammar_var, grammar_var_overrides
from procedural_buildings.parsing.Lexer import Lexer
from procedural_buildings.parsing.Rule import Left, Right, Rule


class TestLexer:
    def test_ident(self):
        tokens = list(Lexer().tokenize("plot"))
        assert len(tokens) == 1
        assert tokens[0].type == "IDENT"
        assert tokens[0].value == "plot"

    def test_comment_stripped(self):
        tokens = list(Lexer().tokenize("plot # this is a comment\n--> I(rect)"))
        assert len(tokens) == 7

    def test_split_keyword(self):
        tokens = list(Lexer().tokenize("split"))
        assert tokens[0].type == "SPLIT"

    def test_float(self):
        tokens = list(Lexer().tokenize("3.14"))
        assert tokens[0].type == "FLOAT"
        assert tokens[0].value == 3.14

    def test_int(self):
        tokens = list(Lexer().tokenize("42"))
        assert tokens[0].type == "INT"
        assert tokens[0].value == 42

    def test_operators(self):
        text = "+ - * / = : --> ~ ( )"
        tokens = list(Lexer().tokenize(text))
        types = [t.type for t in tokens]
        expected = ["PLUS", "MINUS", "TIMES", "DIVIDE", "ASSIGN", "COLON", "ARROW", "TILDE", "LPAR", "RPAR"]
        assert types == expected


class TestGrammarParser:
    def test_parse_simple(self):
        parser = GrammarParser()
        result = parser.parse("plot --> I(rect)\n")
        assert isinstance(result, dict)
        assert len(result) >= 1

    def test_parse_with_vars(self):
        parser = GrammarParser()
        result = parser.parse("h = 3\nplot --> S(~1, ~1, h){I(rect)}\n")
        assert isinstance(result, dict)

    def test_parse_conditional(self):
        parser = GrammarParser()
        result = parser.parse("wall : wallPattern == 1 --> colour(1,0,0){I(rect)}\n")
        assert isinstance(result, dict)


class TestChecker:
    def test_undefined_rule_raises(self):
        checker = Checker()
        with pytest.raises((IndexError, RuntimeError)):
            checker.check({"plot": []})

    def test_checker_accepts_single_rule(self):
        checker = Checker()
        rule = Rule(Left("plot"), Right(OpPrimitive("rect")))
        result = checker.check({"plot": [rule]})
        assert "plot" in result


class TestGrammarVars:
    def test_grammar_var_overrides_default_empty(self):
        result = grammar_var_overrides()
        assert isinstance(result, dict)

    def test_get_grammar_var_returns_fallback(self):
        assert get_grammar_var("nonexistent", 42) == 42

    def test_get_grammar_var_without_override(self):
        assert get_grammar_var("N", 0) == 0
