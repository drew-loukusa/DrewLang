import sys
import os
from drewLexer import DLexer

#lexer = DLexer(sys.argv[0])

# Setup input information:
input = 'print("hello") { } , =  23 *'

# Symbol dict for configuring the lexer to my grammar:
symbols = {
    "NAME":'multi',
    "NUMBER":'multi', 
    "COMMA":',', 
    "LPAREN":'(', 
    "RPAREN":')', 
    "LCURBRACK":'{',
    "RCURBRACK":'}', 
    "SEMICOLON":';',
    "EQUALSIGN":'=', 
    "QUOTE":'"',
    "STAR":"*",
    }

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
lexer = DLexer(input, symbols, multi_char_recognizers)

t = lexer.nextToken()
while t._type != lexer.EOF_TYPE:
    print(t)
    t = lexer.nextToken()
print(t)

print("--------------------------\n", lexer.__dict__)
#print(lexer.__getattribute__("NAME"))



