import os
import sys
from d_lexer import DLexer

# NOTE: I think there's probably a way to generate this recursive decent parser from the grammar file, 
#       but that seems like an exercise for another day. For now, I'm going to hand code this.

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

    def LT(self, i): return self.lookahead[(self.p + i) % self.k] # Circular fetch
    def LA(self, i): return self.LT(i)._type 

    def match(self, x):
        if self.LA(1) == x: # x is token_type 
            self.consume()
        else:
            raise Exception(f"Expecting {self.input.getTokenName(x)}; found {self.LT(1)}.")

    def PROGRAM(self):
        while self.LA(1) != DLexer.EOF:
            self.STATEMENT()
    
    def STATEMENT(self): 
        if self.LA(1) == DLexer.NAME: self.ASSIGNSTAT()
        elif self.LA(1)._text == 'if': self.IFSTAT()
        elif self.LA(1)._text == 'while': self.WHILESTAT()
        elif self.LA(1)._text == 'print': self.PRINTSTAT()
        elif self.LA(1) == DLexer.LCURBRACK: self.BLOCKSTAT()
        
    def ASSIGNSTAT(self):
        self.ID()   ; self.match(DLexer.EQUALS)
        self.EXPR() ; self.match(DLexer.SEMICOLON)

    def PRINTSTAT(self): 
        self.match(DLexer.NAME) ; self.match(DLexer.LPAREN)
        if self.LA(1) == DLexer.NAME: self.ID()
        elif self.LA(1) in [DLexer.QUOTE, DLexer.NUMBER]: self.EXPR
        self.match(DLexer.RPAREN) ; self.match(DLexer.SEMICOLON)
        
    def BLOCKSTAT(self): 
        self.match(DLexer.LCURBRACK); self.STATEMENT(); self.match(DLexer.RCURBRACK)

    def IFSTAT(self): 
        self.match(DLexer.NAME)
        self.match(DLexer.LPAREN)
        self.TEST()
        self.match(DLexer.RPAREN)
        self.STATEMENT()

    def WHILESTAT(self): 
        self.match(DLexer.NAME)
        self.match(DLexer.LPAREN)
        self.TEST()
        self.match(DLexer.RPAREN)
        self.STATEMENT()

    def ID(self): 
        self.match(DLexer.NAME)
        
    def EXPR(self): 
        if self.LA(1) == DLexer.QUOTE: self.STRING()
        elif self.LA(1) == DLexer.NUMBER: self.NUMBER()
        
    def TEST(self): 
        if self.LA(1) == DLexer.NAME: self.ID()
        else: self.EXPR()

        self.CMP_OP()

        if self.LA(1) == DLexer.NAME: self.ID()
        else: self.EXPR()

    def STRING(self):       
        self.match(DLexer.QUOTE)
        # Because I have a token for A-Z and one for 0..9 I have to match both NAME and NUMBERS to parse strings.
        while self.LA(1) in [DLexer.NAME, DLexer.NUMBER]: 
            if self.LA(1) == DLexer.NAME: self.match(DLexer.NAME)
            if self.LA(1) == DLexer.NUMBER: self.match(DLexer.NUMBER)
        self.match(DLexer.QUOTE)

    def NUMBER(self): 
        self.match(DLexer.NUMBER)  

    def CMP_OP(self): 
        # ==
        if self.LA(1) == DLexer.EQUALS and self.LA(2) == DLexer.EQUALS:
            self.match(DLexer.EQUALS); self.match(DLexer.EQUALS)
        # >=
        elif self.LA(1) == DLexer.GT and self.LA(2) == DLexer.EQUALS:
            self.match(DLexer.GT); self.match(DLexer.EQUALS)

        # <=
        elif self.LA(1) == DLexer.LT and self.LA(2) == DLexer.EQUALS:
            self.match(DLexer.LT); self.match(DLexer.EQUALS)
        # >
        elif self.LA(1) == DLexer.GT:self.match(DLexer.GT)
        
        # <
        elif self.LA(1) == DLexer.LT: self.match(DLexer.LT)

        else: 
            raise Exception(f"Expecting a comparison operator; found {self.LT(1)}")