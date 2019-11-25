from d_lexer import DLexer
from ast import AST
import time

# TODO: Add, by hand, AST code to each rule function. 
# 
# 
#       Yes, I will add support to my parser generator to 
#       generate AST code inside each function, but that's a little bit of work. 
#       
#       I'll do that later.

class Parser:
    def __init__(self, input, k):
        self.input = DLexer(input) 
        self.k = k      # How many lookahead tokens
        self.p = 0      # Circular index of next token positon to fill
        self.lookahead = [] # Circular lookahead buffer 
        for _ in range(k): # Prime buffer
            self.lookahead.append(self.input.nextToken())

        self.root = AST() # Abstact syntax tree root node 

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

            If self.LA(1) == x, returns an AST node with token x as the data.
        """
        if type(x) is str: 
            x = self.input.getTokenType(x)
        if self.LA(1) == x: # x is token_type 
            self.consume()
            return AST(self.LT(1)) # Return an AST node created with the current token
        else:
            raise Exception(f"Expecting {self.input.getTokenName(x)}; found {self.LT(1)}.")

    def _add_children_to_root(self, scope_locals, root):
        """ Adds any nodes found in 'scope_locals' to root and returns 'root' AST node.

            'scope_locals' should be locals()
        """
        for name, pnode in scope_locals: # For name, possiblely_a_node in locals()
            if name[0:3] == "node": root.addChild(pnode)
        return root
    
    def program(self):        
        while self.LA(1) != self.input.EOF_TYPE:
            self.root.addChild(self.statement())
    
    def statement(self):
        root = None
        if self.LA(1) == self.input.PRINT:
            root = self.printstat()
        elif self.LA(1) == self.input.LCURBRACK:
            root = self.blockstat()
        elif self.LA(1) == self.input.IF:
            root = self.ifstat()
        elif self.LA(1) == self.input.WHILE:
            root = self.whilestat()
        elif self.LA(1) == self.input.NAME:
            root = self.assignstat()
        elif self.LA(1) == self.input.DEF:
            root =self.funcdef()
        elif self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN:
            root = self.funccall()

        return root
    
    def assignstat(self):
        
        node1 = self.NAME()

        root = self.match('=')

        node2 = None
        if self.LA(1) == self.input.NAME or self.LA(1) == self.input.NUMBER or self.LA(1) == self.input.STRING:
            node2 = self.expr()
        elif self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN:
            node2 = self.funccall()
        self.match(';')

        return self._add_children_to_root(locals(), root)
    
    def printstat(self):
        # Match print, and make 'print' the root AST node             
        root = self.match('print') 
        
        self.match('(')
        
        node1 = None
        if self.LA(1) == self.input.NAME:
            node1 = self.NAME()
        elif self.LA(1) == self.input.NAME or self.LA(1) == self.input.NUMBER or self.LA(1) == self.input.STRING:
            node1 = self.expr()
        self.match(')')
        self.match(';')

        return self._add_children_to_root(locals(), root)

    def ifstat(self):
        root = self.match('if')
        self.match('(')
        node1 = self.test()
        self.match(')')
        node2 = self.statement()

        return self._add_children_to_root(locals(), root)
    
    def whilestat(self):
        root = self.match('while')
        self.match('(')
        node1 = self.test()
        self.match(')')
        node2 = self.statement()
        
        return self._add_children_to_root(locals(), root)
    
    def blockstat(self):
        root = None
        self.match('{')
        while self.LA(1) != self.input.RCURBRACK:
            root = self.statement()
        self.match('}')

        return self._add_children_to_root(locals(), root)

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
    
    
    def expr(self):
        node1 = None
        if self.LA(1) == self.input.NAME:
            node1 = self.NAME()
        elif self.LA(1) == self.input.NUMBER:
            self.NUMBER()
        elif self.LA(1) == self.input.STRING:
            self.STRING()

        # If there are more items, the root will change... 
        # Multiple times maybe. You kinda need a seperate way to handle expressions... 
        while self.LA(1) == self.input.PLUS or self.LA(1) == self.input.DASH:
            self.add_op()
            self.expr()
        
        return self._add_children_to_root(locals(), root)
    
    def test(self):
        node1 = self.expr()
        root  = self.cmp_op()
        node2 = self.expr()

        return self._add_children_to_root(locals(), root)
    
    def funcdef(self):
        root = self.match('def')
        node1 = self.NAME()
        node2 = self.parameters()
        node3 = self.statement()

        return self._add_children_to_root(locals(), root)
    
    def funccall(self):
        root  = self.NAME()
        node1 = self.parameters()
        self.match(';')

        return self._add_children_to_root(locals(), root)
    
    def parameters(self):
        root = AST(artificial=True, name='parameters')
        self.match('(')
        if self.LA(1) == self.input.NAME:
            root.addChild(self.NAME())
        while self.LA(1) == self.input.COMMA:
            self.match(',')
            root.addChild(self.NAME())
        self.match(')')

        return self._add_children_to_root(locals(), root)
    
    def STRING(self):
        return self.match(self.input.STRING)
    
    def NAME(self):
        return self.match(self.input.NAME)
    
    def NUMBER(self):
        return self.match(self.input.NUMBER)
    
    def cmp_op(self):      
        if self.LA(1) == self.input.EQUALS:
            return self.DEQUALS()
        elif self.LA(1) == self.input.GT and self.LA(2) == self.input.EQUALS:
            return self.GE()
        elif self.LA(1) == self.input.LT and self.LA(2) == self.input.EQUALS:
            return self.LE()
        elif self.LA(1) == self.input.GT:
            return self.match('>')
        elif self.LA(1) == self.input.LT:
            return self.match('<')

    def math_op(self):
        if self.LA(1) == self.input.PLUS or self.LA(1) == self.input.DASH:
            return self.add_op()
        elif self.LA(1) == self.input.STAR or self.LA(1) == self.input.FSLASH:
            return self.mult_op()

    def add_op(self):        
        if self.LA(1) == self.input.PLUS:
            return self.match('+')
        elif self.LA(1) == self.input.DASH:
            return self.match('-')

    def mult_op(self):
        if self.LA(1) == self.input.STAR:
            return self.match('*')
        elif self.LA(1) == self.input.FSLASH:
            return self.match('/')
    
    def DEQUALS(self):
        return self.match('==')
    
    def GE(self):
        return self.match('>=')
    
    def LE(self):
        return self.match('<=')

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
