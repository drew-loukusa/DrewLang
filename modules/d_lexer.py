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
     
        