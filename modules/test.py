import sys
#from lexer import Lexer

#lexer = DLexer(sys.argv[0])

# Setup input information:
# input = 'print ( ) { } [] , . : ; =  1 10 - + * \\ / \' " '
# input = 'print("Hello"); x = 0; foo = "bar";'
# # Read in token names and chars to pass into the lexer:
# fpath = "tokens.txt"
# # The order in which you set multi char recognizers here is the order in which the lexer
# # will test the input string. Format: List of tuples: [ (TOKEN_NAME, Recognizer for start of token)]
# multi_char_recognizers = [ 
#     ("NAME", lambda c: (c>= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') # isLetter), 
#     ("NUMBER", lambda c: c >= '0' and c <= '9' # isDigit),
# ]
# # Create lexer object, feed it my input and my symbols. 
# # It will automatically populate an instance with the appropriate fields as needed
# lexer = Lexer(input, fpath, multi_char_recognizers)
# t = lexer.nextToken()
# while t._type != lexer.EOF_TYPE:
#     print(t)
#     t = lexer.nextToken()
# print(t)

#print("--------------------------\n", lexer.__dict__)
#print(lexer.__getattribute__("NAME"))

# from parser import Parser
# drewparser = Parser(sys.argv[0], 2)
# drewparser.PROGRAM()