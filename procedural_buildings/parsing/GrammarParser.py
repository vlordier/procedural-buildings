import re

from .Checker import Checker
from .Lexer import Lexer
from .Parser import Parser
from .ParserAbstract import ParserAbstract


class GrammarParser(ParserAbstract):
    def parse(self, grammar):
        lexer = Lexer()
        parser = Parser()
        checker = Checker()
        if not grammar.endswith("\n"):
            grammar += "\n"
        grammar = re.sub(r"^\d+:\s*", "", grammar, flags=re.MULTILINE)
        tokens = lexer.tokenize(grammar)
        if lexer.errors:
            raise RuntimeError("\n".join(lexer.errors))
        return checker.check(parser.parse(tokens))
