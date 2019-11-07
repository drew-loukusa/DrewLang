
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
    
    def assignstat(self):
        self.match(self.input.NAME)
        self.match(self.input.getTokenType('='))
        self.expr()
        self.match(self.input.getTokenType(';'))
    
    def printstat(self):
        self.match(self.input.getTokenType('print'))
        self.match(self.input.getTokenType('('))
        if self.LA(1) == self.input.NAME:
            self.match(self.input.NAME)
        elif self.LA(1) == self.input.NUMBER or self.LA(1) == self.input.DQUOTE:
            self.expr()
        self.match(self.input.getTokenType(')'))
        self.match(self.input.getTokenType(';'))
    
    def ifstat(self):
        self.match(self.input.getTokenType('if'))
        self.match(self.input.getTokenType('('))
        self.test()
        self.match(self.input.getTokenType(')'))
        self.statement()
    
    def whilestat(self):
        self.match(self.input.getTokenType('while'))
        self.match(self.input.getTokenType('('))
        self.test()
        self.match(self.input.getTokenType(')'))
        self.statement()
    
    def blockstat(self):
        self.match(self.input.getTokenType('{'))
        while self.LA(1) != self.input.RCURBRACK:
            self.statement()
        self.match(self.input.getTokenType('}'))
    
    def expr(self):
        if self.LA(1) == self.input.NUMBER:
            self.match(self.input.NUMBER)
        elif self.LA(1) == self.input.DQUOTE:
            self.STRING()
    
    def test(self):
        if self.LA(1) == self.input.NAME:
            self.match(self.input.NAME)
        elif self.LA(1) == self.input.NUMBER or self.LA(1) == self.input.DQUOTE:
            self.expr()
        self.CMP_OP()
        if self.LA(1) == self.input.NAME:
            self.match(self.input.NAME)
        elif self.LA(1) == self.input.NUMBER or self.LA(1) == self.input.DQUOTE:
            self.expr()
    
    def NAME(self):
        self.match(self.input.NAME)
    
    def STRING(self):
        self.match(self.input.getTokenType('"'))
        while self.LA(1) == self.input.NAME or self.LA(1) == self.input.NUMBER:
            if self.LA(1) == self.input.NAME:
                self.match(self.input.NAME)
            elif self.LA(1) == self.input.NUMBER:
                self.match(self.input.NUMBER)
        self.match(self.input.getTokenType('"'))
    
    def NUMBER(self):
        self.match(self.input.NUMBER)
    
    def CMP_OP(self):
        if self.LA(1) == self.input.EQUALS:
            self.DEQUALS()
        elif self.LA(1) == self.input.GT and self.LA(2) == self.input.EQUALS:
            self.GE()
        elif self.LA(1) == self.input.LT and self.LA(2) == self.input.EQUALS:
            self.LE()
        elif self.LA(1) == self.input.GT:
            self.match(self.input.getTokenType('>'))
        elif self.LA(1) == self.input.LT:
            self.match(self.input.getTokenType('<'))
    
    def DEQUALS(self):
        self.match(self.input.getTokenType('='))
        self.match(self.input.getTokenType('='))
    
    def GE(self):
        self.match(self.input.getTokenType('>'))
        self.match(self.input.getTokenType('='))
    
    def LE(self):
        self.match(self.input.getTokenType('<'))
        self.match(self.input.getTokenType('='))


if __name__ == "__main__":
    import sys
    input = """x=0;
print("Helloworld");
if(x==0){
    print("xis0");
    print(x);
    x=1;
}
"""
    drewparser = Parser(input, 2)
    drewparser.program()
    