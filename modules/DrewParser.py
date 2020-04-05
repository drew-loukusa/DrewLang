from d_lexer import DLexer
from ast import AST
import time

class Parser:    
    def __init__(self, input, k, path_to_grammar_file):
        self.input = DLexer(input, path_to_grammar_file)         
        self.k = k      # How many lookahead tokens
        self.p = 0      # Circular index of next token positon to fill
        self.lookahead = [] # Circular lookahead buffer 
        for _ in range(k): # Prime buffer
            self.lookahead.append(self.input.nextToken())

    def consume(self):
        self.lookahead[self.p] = self.input.nextToken()
        self.p = (self.p+1) % self.k 

    def LT(self, i):         
        return self.lookahead[(self.p + i - 1) % self.k] # Circular fetch
    def LA(self, i): return self.LT(i)._type 

    def match(self, x):
        """ Accepts token_type (int) or the token char.
            Example: 
                    token_type: 7      (I think)
                    token_char: '('
        """
        if type(x) is str: 
            x = self.input.getTokenType(x)
        if self.LA(1) == x: # x is token_type 
            ast_node = AST(self.LT(1)) # Return an AST node created with the current token
            self.consume()
            return ast_node
        else:
            raise Exception(f"Expecting {self.input.getTokenName(x)}; found {self.LT(1)} on line # {self.LT(1)._line_number}")            
if __name__ == "__main__":
    import os 
    import sys
    input = \
"""x=0;
print("Helloworld");
if(x==0){
    print("xis0");
    print(x);
    x=1;
}
"""
    from locate_file import check_cache_or_find
    # Get path to grammar file: 
    grammar_file_name = "DrewGrammar.txt"
    grammar_file_path = check_cache_or_find(grammar_file_name, start_dir="C:\\Users", path_cache_file="paths.txt")

    cwd = os.getcwd()[0:-8]
    #drewparser = Parser(input, 2, grammar_file_path) 
    drewparser = Parser(input, 2, grammar_file_path)
    AST = drewparser.program()
    AST.toStringTree()
