from lexer import Lexer 

class DLexer(Lexer):
    def __init__(self, input):
        # cons
        fpath="tokens.txt"
        token_defs = { l.split()[0]:l.split()[1] for l in open(fpath).readlines() }
        # Functions to configure the lexer
        isLetter = lambda c: (c>= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z')
        isDigit  = lambda c: c >= '0' and c <= '9'
        multi_char_recognizers = [ ("NAME", isLetter), ("NUMBER", isDigit) ]
        super().__init__(input, token_defs, multi_char_recognizers)        
     # Read in token names and chars to pass into the lexer:
        