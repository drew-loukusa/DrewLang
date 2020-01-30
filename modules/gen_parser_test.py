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
    
    def program(self):
        root, lnodes = None, []
        root = AST(name='PROGRAM', artificial=True)
        while self.LA(1) == self.input.PRINT or self.LA(1) == self.input.LCURBRACK or self.LA(1) == self.input.IF or self.LA(1) == self.input.WHILE or  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.EQUALS)  or self.LA(1) == self.input.DEF or  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN)  or self.LA(1) == self.input.DO or self.LA(1) == self.input.NAME or self.LA(1) == self.input.NUMBER or self.LA(1) == self.input.STRING or  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN) :
            lnodes.append( self.statement() )
        if root: root.children.extend(lnodes); return root
        else: return lnodes[0]
    
    def statement(self):
        root, lnodes = None, []
        if self.LA(1) == self.input.PRINT:
            temp = root
            root = self.printstat()
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.LCURBRACK:
            temp = root
            root = self.blockstat()
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.IF:
            temp = root
            root = self.ifstat()
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.WHILE:
            temp = root
            root = self.whilestat()
            if temp: root.addChild(temp) 
        elif  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.EQUALS) :
            temp = root
            root = self.assignstat()
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.DEF:
            temp = root
            root = self.funcdef()
            if temp: root.addChild(temp) 
        elif  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN) :
            temp = root
            root = self.funccall()
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.DO:
            temp = root
            root = self.dowhile()
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.NAME or self.LA(1) == self.input.NUMBER or self.LA(1) == self.input.STRING or  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN) :
            temp = root
            root = self.exprstat()
            if temp: root.addChild(temp) 
        else: raise Exception(f"Expecting something; found {self.LT(1)} on Line {self.LT(1)._line_number}.")
        if root: root.children.extend(lnodes); return root
        else: return lnodes[0]
    
    def assignstat(self):
        root, lnodes = None, []
        lnodes.append( self.match(self.input.NAME) )
        root = self.match('=')
        lnodes.append( self.expr() )
        self.match(';')
        if root: root.children.extend(lnodes); return root
        else: return lnodes[0]
    
    def printstat(self):
        root, lnodes = None, []
        root = self.match('print')
        self.match('(')
        lnodes.append( self.expr() )
        self.match(')')
        self.match(';')
        if root: root.children.extend(lnodes); return root
        else: return lnodes[0]
    
    def ifstat(self):
        root, lnodes = None, []
        root = self.match('if')
        self.match('(')
        lnodes.append( self.test() )
        self.match(')')
        lnodes.append( self.statement() )
        if root: root.children.extend(lnodes); return root
        else: return lnodes[0]
    
    def whilestat(self):
        root, lnodes = None, []
        root = self.match('while')
        self.match('(')
        lnodes.append( self.test() )
        self.match(')')
        lnodes.append( self.statement() )
        if root: root.children.extend(lnodes); return root
        else: return lnodes[0]
    
    def blockstat(self):
        root, lnodes = None, []
        root = AST(name='BLOCKSTAT', artificial=True)
        self.match('{')
        while self.LA(1) != self.input.RCURBRACK:
            lnodes.append( self.statement() )
        self.match('}')
        if root: root.children.extend(lnodes); return root
        else: return lnodes[0]
    
    def exprstat(self):
        root, lnodes = None, []
        root = self.expr()
        self.match(';')
        if root: root.children.extend(lnodes); return root
        else: return lnodes[0]
    
    def dowhile(self):
        root, lnodes = None, []
        root = self.match('do')
        lnodes.append( self.blockstat() )
        self.match('while')
        self.match('(')
        lnodes.append( self.test() )
        self.match(')')
        if root: root.children.extend(lnodes); return root
        else: return lnodes[0]
    
    def expr(self):
        root, lnodes = None, []
        lnodes.append( self.term() )
        while self.LA(1) == self.input.PLUS or self.LA(1) == self.input.DASH:
            temp = root
            root = self.add_op()
            if temp: root.addChild(temp) 
            lnodes.append( self.term() )
        if root: root.children.extend(lnodes); return root
        else: return lnodes[0]
    
    def term(self):
        root, lnodes = None, []
        lnodes.append( self.atom() )
        while self.LA(1) == self.input.STAR or self.LA(1) == self.input.FSLASH:
            temp = root
            root = self.mult_op()
            if temp: root.addChild(temp) 
            lnodes.append( self.atom() )
        if root: root.children.extend(lnodes); return root
        else: return lnodes[0]
    
    def atom(self):
        root, lnodes = None, []
        if self.LA(1) == self.input.NAME:
            temp = root
            root = self.match(self.input.NAME)
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.NUMBER:
            temp = root
            root = self.match(self.input.NUMBER)
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.STRING:
            temp = root
            root = self.match(self.input.STRING)
            if temp: root.addChild(temp) 
        elif  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN) :
            temp = root
            root = self.funccall()
            if temp: root.addChild(temp) 
        else: raise Exception(f"Expecting something; found {self.LT(1)} on Line {self.LT(1)._line_number}.")
        if root: root.children.extend(lnodes); return root
        else: return lnodes[0]
    
    def test(self):
        root, lnodes = None, []
        lnodes.append( self.expr() )
        root = self.cmp_op()
        lnodes.append( self.expr() )
        if root: root.children.extend(lnodes); return root
        else: return lnodes[0]
    
    def funcdef(self):
        root, lnodes = None, []
        root = self.match('def')
        lnodes.append( self.match(self.input.NAME) )
        self.match('(')
        if self.LA(1) == self.input.NAME or self.LA(1) == self.input.NUMBER or self.LA(1) == self.input.STRING or  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN) :
            lnodes.append( self.exprlist() )
        self.match(')')
        lnodes.append( self.statement() )
        if root: root.children.extend(lnodes); return root
        else: return lnodes[0]
    
    def funccall(self):
        root, lnodes = None, []
        root = self.match(self.input.NAME)
        self.match('(')
        if self.LA(1) == self.input.NAME or self.LA(1) == self.input.NUMBER or self.LA(1) == self.input.STRING or  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN) :
            lnodes.append( self.exprlist() )
        self.match(')')
        self.match(';')
        if root: root.children.extend(lnodes); return root
        else: return lnodes[0]
    
    def exprlist(self):
        root, lnodes = None, []
        root = AST(name='EXPRLIST', artificial=True)
        lnodes.append( self.expr() )
        while self.LA(1) == self.input.COMMA:
            self.match(',')
            lnodes.append( self.expr() )
        if root: root.children.extend(lnodes); return root
        else: return lnodes[0]
    
    def cmp_op(self):
        root, lnodes = None, []
        if self.LA(1) == self.input.DEQUALS:
            temp = root
            root = self.match('==')
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.GE:
            temp = root
            root = self.match('>=')
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.LE:
            temp = root
            root = self.match('<=')
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.GT:
            temp = root
            root = self.match('>')
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.LT:
            temp = root
            root = self.match('<')
            if temp: root.addChild(temp) 
        else: raise Exception(f"Expecting something; found {self.LT(1)} on Line {self.LT(1)._line_number}.")
        if root: root.children.extend(lnodes); return root
        else: return lnodes[0]
    
    def add_op(self):
        root, lnodes = None, []
        if self.LA(1) == self.input.PLUS:
            temp = root
            root = self.match('+')
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.DASH:
            temp = root
            root = self.match('-')
            if temp: root.addChild(temp) 
        else: raise Exception(f"Expecting something; found {self.LT(1)} on Line {self.LT(1)._line_number}.")
        if root: root.children.extend(lnodes); return root
        else: return lnodes[0]
    
    def mult_op(self):
        root, lnodes = None, []
        if self.LA(1) == self.input.STAR:
            temp = root
            root = self.match('*')
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.FSLASH:
            temp = root
            root = self.match('/')
            if temp: root.addChild(temp) 
        else: raise Exception(f"Expecting something; found {self.LT(1)} on Line {self.LT(1)._line_number}.")
        if root: root.children.extend(lnodes); return root
        else: return lnodes[0]
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
do{
    print("A test");
} while(x == 0)
"""

    cwd = os.getcwd() 
    #drewparser = Parser(input, 2, cwd + "\\grammar_grammar.txt") 
    drewparser = Parser(input, 2, cwd + "\\DrewGrammar.txt")
    AST = drewparser.program()
    AST.toStringTree()
