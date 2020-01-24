from d_lexer import DLexer
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
            self.consume()
        else:
            raise Exception(f"Expecting {self.input.getTokenName(x)}; found {self.LT(1)} on line # {self.LT(1)._line_number}")            
    
    def program(self):
        while self.LA(1) == self.input.PRINT or self.LA(1) == self.input.LCURBRACK or self.LA(1) == self.input.IF or self.LA(1) == self.input.WHILE or  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.EQUALS)  or self.LA(1) == self.input.DEF or  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN)  or self.LA(1) == self.input.NAME or self.LA(1) == self.input.NUMBER or self.LA(1) == self.input.STRING or  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN) :
            self.statement()
    
    def statement(self):
        if self.LA(1) == self.input.PRINT:
            self.printstat()
        elif self.LA(1) == self.input.LCURBRACK:
            self.blockstat()
        elif self.LA(1) == self.input.IF:
            self.ifstat()
        elif self.LA(1) == self.input.WHILE:
            self.whilestat()
        elif  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.EQUALS) :
            self.assignstat()
        elif self.LA(1) == self.input.DEF:
            self.funcdef()
        elif  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN) :
            self.funccall()
        elif self.LA(1) == self.input.NAME or self.LA(1) == self.input.NUMBER or self.LA(1) == self.input.STRING or  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN) :
            self.exprstat()
        else: raise Exception(f"Expecting something; found {self.LT(1)} on Line {self.LT(1)._line_number}.")
    
    def assignstat(self):
        self.match(self.input.NAME)
        self.match('=')
        self.expr()
        self.match(';')
    
    def printstat(self):
        self.match('print')
        self.match('(')
        self.expr()
        self.match(')')
        self.match(';')
    
    def ifstat(self):
        self.match('if')
        self.match('(')
        self.test()
        self.match(')')
        self.statement()
    
    def whilestat(self):
        self.match('while')
        self.match('(')
        self.test()
        self.match(')')
        self.statement()
    
    def blockstat(self):
        self.match('{')
        while self.LA(1) != self.input.RCURBRACK:
            self.statement()
        self.match('}')
    
    def exprstat(self):
        self.expr()
        self.match(';')
    
    def expr(self):
        self.term()
        while self.LA(1) == self.input.PLUS or self.LA(1) == self.input.DASH:
            self.add_op()
            self.term()
    
    def term(self):
        self.atom()
        while self.LA(1) == self.input.STAR or self.LA(1) == self.input.FSLASH:
            self.mult_op()
            self.atom()
    
    def atom(self):
        if self.LA(1) == self.input.NAME:
            self.match(self.input.NAME)
        elif self.LA(1) == self.input.NUMBER:
            self.match(self.input.NUMBER)
        elif self.LA(1) == self.input.STRING:
            self.match(self.input.STRING)
        elif  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN) :
            self.funccall()
        else: raise Exception(f"Expecting something; found {self.LT(1)} on Line {self.LT(1)._line_number}.")
    
    def test(self):
        self.expr()
        self.cmp_op()
        self.expr()
    
    def funcdef(self):
        self.match('def')
        self.match(self.input.NAME)
        self.parameters()
        self.statement()
    
    def funccall(self):
        self.match(self.input.NAME)
        self.parameters()
        self.match(';')
    
    def parameters(self):
        self.match('(')
        if self.LA(1) == self.input.NAME or self.LA(1) == self.input.NUMBER or self.LA(1) == self.input.STRING or  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN) :
            self.exprlist()
        self.match(')')
    
    def exprlist(self):
        self.expr()
        while self.LA(1) == self.input.COMMA:
            self.match(',')
            self.expr()
    
    def cmp_op(self):
        if self.LA(1) == self.input.DEQUALS:
            self.match('==')
        elif self.LA(1) == self.input.GE:
            self.match('>=')
        elif self.LA(1) == self.input.LE:
            self.match('<=')
        elif self.LA(1) == self.input.GT:
            self.match('>')
        elif self.LA(1) == self.input.LT:
            self.match('<')
        else: raise Exception(f"Expecting something; found {self.LT(1)} on Line {self.LT(1)._line_number}.")
    
    def add_op(self):
        if self.LA(1) == self.input.PLUS:
            self.match('+')
        elif self.LA(1) == self.input.DASH:
            self.match('-')
        else: raise Exception(f"Expecting something; found {self.LT(1)} on Line {self.LT(1)._line_number}.")
    
    def mult_op(self):
        if self.LA(1) == self.input.STAR:
            self.match('*')
        elif self.LA(1) == self.input.FSLASH:
            self.match('/')
        else: raise Exception(f"Expecting something; found {self.LT(1)} on Line {self.LT(1)._line_number}.")
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

    cwd = os.getcwd() 
    #drewparser = Parser(input, 2, cwd + "\\grammar_grammar.txt") 
    drewparser = Parser(input, 2, cwd + "\\DrewGrammar.txt")
    drewparser.program()
