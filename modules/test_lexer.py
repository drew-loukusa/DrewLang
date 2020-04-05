from lexer import Lexer, Token
from locate_file import check_cache_or_find, find, find_dir

#grammar_fpath = find("DrewGrammar.txt", start_dir="C:\\Users")
#grammar_fpath = check_cache_or_find("DrewGrammar.txt", start_dir="C:\\Users", path_cache_file="paths.txt")
grammar_fpath = "C:\\Users\\Drew\\Desktop\\Code Projects\\DrewLangPlayground\\DrewLang\\docs\\DrewGrammar.txt"

tokens = """
BANG                    !
COMMA                   ,
PERIOD                  .
LPAREN                  (
RPAREN                  )
LCURBRACK               {
RCURBRACK               }  
LBRACK                  [
RBRACK                  ]
SEMICOLON               ;
COLON                   :
EQUALS                  =
DEQUALS                 ==
GT                      >
GE                      >=
LT                      < 
LE                      <=  
QUOTE                   ""
DQUOTE                  "
STAR                    *
PLUS                    +
DASH                    -
FSLASH                  /
BSLASH                  \\
IF                      if 
ELIF                    elif 
ELSE                    else
DO                      do 
AND                     and
OR                      or 
WHILE                   while
PRINT                   print
DEF                     def
CLASS                   class
TRUE                    True 
FALSE                   False 
NAME                    test_Name-name
NUMBER                  6956
STRING                  \"A_String!\"
"""

def test_lexer():
    token_string_dict = {}
    for line in tokens.split('\n'):                 
        if len(pair := line.split()) == 2:
            name, string = line.split()
            token_string_dict[name] = string 

    #print(token_string_dict)

    import time 
    test_lexer = Lexer(input=' ', fpath=grammar_fpath)        
    for name, string in token_string_dict.items():
        #print("Help me"); time.sleep(0.1)
        test_lexer.input = list(string)
        test_lexer.p = 0
        test_lexer.c = test_lexer.input[0]
        token = test_lexer.nextToken()

        assert token._tname == name 

       
if __name__ == "__main__":
    test_lexer()
