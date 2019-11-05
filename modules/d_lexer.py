from lexer import Lexer 

""" This module contains a lexer for use with my language which is used by my parser to 
    retrieve tokens from the input string. 
    
    The DLexer lexing class is a configured version of the Lexer class it inherits from.
    
    For more details, see the Lexer class in the lexer.py module"""

class DLexer(Lexer):
    def __init__(self, input):

        # Token defitions file location:
        fpath="token_defs.txt"

        # Functions for lexer to use when lexing multichar tokens:
        isLetter = lambda c: (c>= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z')
        isDigit  = lambda c: c >= '0' and c <= '9'
        multi_char_recognizers = [ ("NAME", isLetter), ("NUMBER", isDigit) ]

        super().__init__(input, fpath, multi_char_recognizers)        
     
        
    # NOTE: The below line is just so I have member names to reference since I dynamically create my lexer at runtime.
    NAME, NUMBER, COMMA, PERIOD, LPAREN, RPAREN, LCURBRACK, RCURBRACK, LBRACK, \
    LBRACK, RBRACK, SEMICOLON, COLON, EQUALS, GT, LT, QUOTE, DQOUTE, STAR, \
    PLUS, DASH, FSLASH, BSLASH = 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0