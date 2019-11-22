from lexer import Lexer 

""" This module contains a lexer for use with my language which is used by my parser to 
    retrieve tokens from the input string. 
    
    The DLexer lexing class is a configured version of the Lexer class it inherits from.
    
    For more details, see the Lexer class in the lexer.py module"""

class DLexer(Lexer):
    # NOTE: The below line is just so I have member names to reference since I dynamically create my lexer at runtime.
    give_nums = lambda: list(range(1,29))
    NAME, NUMBER, COMMA, PERIOD, LPAREN, RPAREN, LCURBRACK, RCURBRACK, LBRACK, \
    LBRACK, RBRACK, SEMICOLON, COLON, EQUALS, GT, LT, QUOTE, DQUOTE, STAR, \
    PLUS, DASH, FSLASH, BSLASH, IF, WHILE, PRINT, DEF, STRING = give_nums()
    def __init__(self, input):

        # Token defitions file location:
        fpath="DrewGrammar.txt"

        # Functions for lexer to use when lexing multichar tokens:
        isLetter = lambda c: (c>= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z')
        isDigit  = lambda c: c >= '0' and c <= '9'
        isStringSOQ = lambda c: c == '"'
        isStringBM  = lambda c: c != '"'
        mcrs = [ 
                    ("NAME", (isLetter, isLetter, None)), 
                    ("NUMBER", (isDigit, isDigit, None)), 
                   ("STRING", (isStringSOQ, isStringBM, isStringSOQ))
                ]

       

        super().__init__(input, fpath, mcrs)

if __name__ == "__main__":
    input = \
"""x=0;
print("Hello world");
if(x>=0){
    print("xis0");
    x=1;

    if ( x == 0 ) print("Fuck yeah");
}
"""
    lexer = DLexer(input) 
    #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    #print("DLexer Class after initialization:")
    #for k,v in lexer.__dict__.items(): print(f"{k}\t: {v}")

    t = lexer.nextToken()
    i = 0
    while t._type != lexer.EOF_TYPE:
        print(i, '\t', t)
        t = lexer.nextToken()
        i+=1
    print(t)


