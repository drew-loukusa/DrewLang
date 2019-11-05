from d_lexer import DLexer
import time
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

        print("~"*20)
        print(*self.lookahead)
        print("~"*20)

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

    def PROGRAM(self):
        while self.LA(1) != self.input.EOF_TYPE:
            print(f"EOF: {self.input.EOF}")
            print("Top level statement call")
            self.STATEMENT()
    
    def STATEMENT(self): 
        print("STATEMENT", self.LT(1), self.LA(1))
        time.sleep(0.5)
        if self.LT(1)._text == 'if': self.IFSTAT()
        elif self.LT(1)._text == 'while': self.WHILESTAT()
        elif self.LT(1)._text == 'print': self.PRINTSTAT()
        elif self.LA(1) == self.input.NAME: self.ASSIGNSTAT()
        elif self.LA(1) == self.input.LCURBRACK: self.BLOCKSTAT()
        
    def ASSIGNSTAT(self):
        print("ASSIGNSTAT", self.LT(1))
        time.sleep(0.5)
        self.ID()   ;print(self.LT(1))
        self.match(self.input.EQUALS) 
        self.EXPR() 
        self.match(self.input.SEMICOLON)

    def PRINTSTAT(self): 
        print("PRINTSTAT", self.LT(1))
        time.sleep(0.5)
        self.match(self.input.NAME)     ;print(self.LT(1))
        self.match(self.input.LPAREN)   ;print(self.LT(1))

        if self.LA(1) == self.input.NAME:
            print("found ID")
            self.ID()

        elif self.LA(1) == self.input.DQUOTE or \
             self.LA(1) == self.input.NUMBER:
            print("Found expr")
            self.EXPR()
        
        self.match(self.input.RPAREN)       
        self.match(self.input.SEMICOLON)    
        
    def BLOCKSTAT(self): 
        print("BLOCKSTAT", self.LT(1))
        time.sleep(0.5)
        self.match(self.input.LCURBRACK); self.STATEMENT(); self.match(self.input.RCURBRACK)

    def IFSTAT(self): 
        print("IFTSTAT", self.LT(1))
        time.sleep(0.5)
        self.match(self.input.NAME)
        self.match(self.input.LPAREN)
        self.TEST()
        self.match(self.input.RPAREN)
        self.STATEMENT()

    def WHILESTAT(self): 
        self.match(self.input.NAME)
        self.match(self.input.LPAREN)
        self.TEST()
        self.match(self.input.RPAREN)
        self.STATEMENT()

    def ID(self): 
        print("ID", self.LT(1))
        time.sleep(0.5)
        self.match(self.input.NAME)
        
    def EXPR(self): 
        print("EXPR",self.LT(1))
        if self.LA(1) == self.input.DQUOTE: self.STRING()
        elif self.LA(1) == self.input.NUMBER: self.NUMBER()
        print(self.LT(1))
        
    def TEST(self): 
        print("TEST", self.LT(1))
        time.sleep(0.5)
        if self.LA(1) == self.input.NAME: self.ID()
        else: self.EXPR()

        self.CMP_OP()

        if self.LA(1) == self.input.NAME: self.ID()
        else: self.EXPR()

    def STRING(self):   
        print("STRING", self.LT(1))
        time.sleep(0.5)    
        self.match(self.input.DQUOTE)
        # Because I have a token for A-Z and one for 0..9 I have to match both NAME and NUMBERS to parse strings.
        while self.LA(1) in [self.input.NAME, self.input.NUMBER]: 
            if self.LA(1) == self.input.NAME: self.match(self.input.NAME)
            if self.LA(1) == self.input.NUMBER: self.match(self.input.NUMBER)
        self.match(self.input.DQUOTE)

    def NUMBER(self): 
        self.match(self.input.NUMBER)  

    def CMP_OP(self): 
        # ==
        if self.LA(1) == self.input.EQUALS and self.LA(2) == self.input.EQUALS:
            self.match(self.input.EQUALS); self.match(self.input.EQUALS)
        # >=
        elif self.LA(1) == self.input.GT and self.LA(2) == self.input.EQUALS:
            self.match(self.input.GT); self.match(self.input.EQUALS)

        # <=
        elif self.LA(1) == self.input.LT and self.LA(2) == self.input.EQUALS:
            self.match(self.input.LT); self.match(self.input.EQUALS)
        # >
        elif self.LA(1) == self.input.GT:self.match(self.input.GT)
        
        # <
        elif self.LA(1) == self.input.LT: self.match(self.input.LT)

        else: 
            raise Exception(f"Expecting a comparison operator; found {self.LT(1)}")

if __name__ == "__main__":
    import sys
    input = \
"""x=0;
print("Helloworld");
if(x==0){
    print("xis0");
}
"""
    drewparser = Parser(input, 2)
    drewparser.PROGRAM()