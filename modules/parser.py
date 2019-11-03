import os
import sys
from d_lexer import DLexer

class Parser:
    def __init__(self, input):
        self.lexer = DLexer(input)

    