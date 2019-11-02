import os
import sys
from drewLexer import Lexer

# Setup input information:
#input = 'print ( ) { } [] , . : ; =  1 10 - + * \\ / \' " '
input = sys.argv[0]

# Read in token names and chars to pass into the lexer:
fpath = "tokens.txt"
symbols = { l.split()[0] : l.split()[1] for l in open(fpath).readlines() }

# The order in which you set multi char recognizers here is the order in which the lexer
# will test the input string. Format: List of tuples: [ (TOKEN_NAME, Recognizer for start of token)]
multi_char_recognizers = [ 
    (
        "NAME", lambda c: (c>= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') # isLetter
    ), 
    (
        "NUMBER", lambda c: c >= '0' and c <= '9' # isDigit
    ),
]

# Create lexer object, feed it my input and my symbols. 
# It will automatically populate an instance with the appropriate fields as needed
lexer = Lexer(input, symbols, multi_char_recognizers)