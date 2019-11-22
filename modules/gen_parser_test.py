from d_lexer import DLexer
import time

class Parser:
    def __init__(self, input, k):
        self.input = DLexer(input) 
        self.k = k      # How many lookahead tokens
        self.p = 0      # Circular index of next token positon to fill
        self.lookahead = [] # Circular lookahead buffer 
        for _ in range(k): # Prime buffer
            self.lookahead.append(self.input.nextToken())

    def consume(self):
        self.lookahead[self.p] = self.input.nextToken()
        self.p = (self.p+1) % self.k 

    def LT(self, i): 
        #print("Hey", i)
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
            raise Exception(f"Expecting {self.input.getTokenName(x)}; found {self.LT(1)}.")
    
    def program(self):
        while self.LA(1) != self.input.EOF_TYPE:
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
        elif self.LA(1) == self.input.NAME:
            self.assignstat()
        elif self.LA(1) == self.input.DEF:
            self.funcdef()
        elif self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN:
            self.funccall()
    
    def assignstat(self):
        self.NAME()
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
    
    def expr(self):
        self.sub_expr()
        while self.LA(1) == self.input.PLUS or self.LA(1) == self.input.DASH or self.LA(1) == self.input.STAR or self.LA(1) == self.input.FSLASH:
            self.math_op()
            self.sub_expr()
    
    def sub_expr(self):
        if self.LA(1) == self.input.NAME:
            self.NAME()
        elif self.LA(1) == self.input.NUMBER:
            self.NUMBER()
        elif self.LA(1) == self.input.STRING:
            self.STRING()
        elif self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN:
            self.funccall()
    
    def test(self):
        self.expr()
        self.cmp_op()
        self.expr()
    
    def funcdef(self):
        self.match('def')
        self.NAME()
        self.parameters()
        self.statement()
    
    def funccall(self):
        self.NAME()
        self.parameters()
        self.match(';')
    
    def parameters(self):
        self.match('(')
        while self.LA(1) == self.input.NAME:
            self.NAME()
        while self.LA(1) == self.input.COMMA:
            self.match(',')
            self.NAME()
        self.match(')')
    
    def STRING(self):
        self.match(self.input.STRING)
    
    def NAME(self):
        self.match(self.input.NAME)
    
    def NUMBER(self):
        self.match(self.input.NUMBER)
    
    def cmp_op(self):
        if self.LA(1) == self.input.EQUALS:
            self.DEQUALS()
        elif self.LA(1) == self.input.GT and self.LA(2) == self.input.EQUALS:
            self.GE()
        elif self.LA(1) == self.input.LT and self.LA(2) == self.input.EQUALS:
            self.LE()
        elif self.LA(1) == self.input.GT:
            self.match('>')
        elif self.LA(1) == self.input.LT:
            self.match('<')
    
    def math_op(self):
        if self.LA(1) == self.input.PLUS or self.LA(1) == self.input.DASH:
            self.add_op()
        elif self.LA(1) == self.input.STAR or self.LA(1) == self.input.FSLASH:
            self.mult_op()
    
    def add_op(self):
        if self.LA(1) == self.input.PLUS:
            self.match('+')
        elif self.LA(1) == self.input.DASH:
            self.match('-')
    
    def mult_op(self):
        if self.LA(1) == self.input.STAR:
            self.match('*')
        elif self.LA(1) == self.input.FSLASH:
            self.match('/')
    
    def DEQUALS(self):
        self.match('=')
        self.match('=')
    
    def GE(self):
        self.match('>')
        self.match('=')
    
    def LE(self):
        self.match('<')
        self.match('=')
if __name__ == "__main__":
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
    drewparser = Parser(input, 2)
    drewparser.program()
