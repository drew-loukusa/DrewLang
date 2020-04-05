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
        root.name = "$PROGRAM"
        while self.LA(1) == self.input.PRINT or self.LA(1) == self.input.LCURBRACK or self.LA(1) == self.input.IF or self.LA(1) == self.input.WHILE or  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.EQUALS)  or self.LA(1) == self.input.DEF or  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN)  or self.LA(1) == self.input.DO or self.LA(1) == self.input.CLASS or self.LA(1) == self.input.LPAREN or self.LA(1) == self.input.NAME or self.LA(1) == self.input.NUMBER or self.LA(1) == self.input.STRING or  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN)  or self.LA(1) == self.input.NAME or self.LA(1) == self.input.TRUE or self.LA(1) == self.input.FALSE or self.LA(1) == self.input.DASH or self.LA(1) == self.input.BANG:
            lnodes.append( self.statement() )
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def statement(self):
        root, lnodes = None, []
        if self.LA(1) == self.input.PRINT:
            temp = root
            root = self.printstat()
            root.name = "printstat"
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.LCURBRACK:
            temp = root
            root = self.blockstat()
            root.name = "blockstat"
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.IF:
            temp = root
            root = self.ifstat()
            root.name = "ifstat"
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.WHILE:
            temp = root
            root = self.whilestat()
            root.name = "whilestat"
            if temp: root.addChild(temp) 
        elif  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.EQUALS) :
            temp = root
            root = self.assignstat()
            root.name = "assignstat"
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.DEF:
            temp = root
            root = self.funcdef()
            root.name = "funcdef"
            if temp: root.addChild(temp) 
        elif  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN) :
            temp = root
            root = self.funccall()
            root.name = "funccall"
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.DO:
            temp = root
            root = self.dowhile()
            root.name = "dowhile"
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.CLASS:
            temp = root
            root = self.classdef()
            root.name = "classdef"
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.LPAREN or self.LA(1) == self.input.NAME or self.LA(1) == self.input.NUMBER or self.LA(1) == self.input.STRING or  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN)  or self.LA(1) == self.input.NAME or self.LA(1) == self.input.TRUE or self.LA(1) == self.input.FALSE or self.LA(1) == self.input.DASH or self.LA(1) == self.input.BANG:
            temp = root
            root = self.exprstat()
            root.name = "exprstat"
            if temp: root.addChild(temp) 
        else: raise Exception(f"Expecting something; found {self.LT(1)} on Line {self.LT(1)._line_number}.")
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def suite_stat(self):
        root, lnodes = None, []
        if  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN) :
            temp = root
            root = self.funccall()
            root.name = "funccall"
            if temp: root.addChild(temp) 
        elif  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.EQUALS) :
            temp = root
            root = self.assignstat()
            root.name = "assignstat"
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.LCURBRACK:
            temp = root
            root = self.blockstat()
            root.name = "blockstat"
            if temp: root.addChild(temp) 
        else: raise Exception(f"Expecting something; found {self.LT(1)} on Line {self.LT(1)._line_number}.")
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def assignstat(self):
        root, lnodes = None, []
        lnodes.append( self.match(self.input.NAME) )
        root = self.match('=')
        root.name = "'='"
        lnodes.append( self.expr() )
        self.match(';')
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def blockstat(self):
        root, lnodes = None, []
        root = AST(name='BLOCKSTAT', artificial=True)
        root.name = "$BLOCKSTAT"
        self.match('{')
        while self.LA(1) != self.input.RCURBRACK:
            lnodes.append( self.statement() )
        self.match('}')
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def printstat(self):
        root, lnodes = None, []
        root = self.match('print')
        root.name = "'print'"
        self.match('(')
        lnodes.append( self.expr() )
        self.match(')')
        self.match(';')
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def ifstat(self):
        root, lnodes = None, []
        root = self.match('if')
        root.name = "'if'"
        lnodes.append( self.test() )
        lnodes.append( self.suite_stat() )
        if self.LA(1) == self.input.STAR:
            lnodes.append( self.elif_else_stat() )
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def elif_else_stat(self):
        root, lnodes = None, []
        root = AST(name='ELIF_ELSE_STAT', artificial=True)
        root.name = "$ELIF_ELSE_STAT"
        while self.LA(1) != self.input.ELSE:
            lnodes.append( self.elifstat() )
        if self.LA(1) == self.input.ELSE:
            lnodes.append( self.elsestat() )
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def elifstat(self):
        root, lnodes = None, []
        root = self.match('elif')
        root.name = "'elif'"
        lnodes.append( self.test() )
        lnodes.append( self.suite_stat() )
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def elsestat(self):
        root, lnodes = None, []
        root = self.match('else')
        root.name = "'else'"
        lnodes.append( self.suite_stat() )
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def whilestat(self):
        root, lnodes = None, []
        root = self.match('while')
        root.name = "'while'"
        lnodes.append( self.test() )
        lnodes.append( self.suite_stat() )
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def dowhile(self):
        root, lnodes = None, []
        root = self.match('do')
        root.name = "'do'"
        lnodes.append( self.blockstat() )
        self.match('while')
        lnodes.append( self.test() )
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def exprstat(self):
        root, lnodes = None, []
        root = self.expr()
        root.name = "expr"
        self.match(';')
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def classdef(self):
        root, lnodes = None, []
        root = self.match('class')
        root.name = "'class'"
        lnodes.append( self.match(self.input.NAME) )
        lnodes.append( self.blockstat() )
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def expr(self):
        root, lnodes = None, []
        if self.LA(1) == self.input.LPAREN:
            temp = root
            root = self.grouping()
            root.name = "grouping"
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.NAME or self.LA(1) == self.input.NUMBER or self.LA(1) == self.input.STRING or  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN)  or self.LA(1) == self.input.NAME or self.LA(1) == self.input.TRUE or self.LA(1) == self.input.FALSE:
            temp = root
            root = self.add_expr()
            root.name = "add_expr"
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.DASH or self.LA(1) == self.input.BANG:
            temp = root
            root = self.negate_expr()
            root.name = "negate_expr"
            if temp: root.addChild(temp) 
        else: raise Exception(f"Expecting something; found {self.LT(1)} on Line {self.LT(1)._line_number}.")
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def grouping(self):
        root, lnodes = None, []
        self.match('(')
        root = self.expr()
        root.name = "expr"
        self.match(')')
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def negate_expr(self):
        root, lnodes = None, []
        if self.LA(1) == self.input.DASH:
            temp = root
            root = self.match('-')
            root.name = "'-'"
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.BANG:
            temp = root
            root = self.match('!')
            root.name = "'!'"
            if temp: root.addChild(temp) 
        else: raise Exception(f"Expecting something; found {self.LT(1)} on Line {self.LT(1)._line_number}.")
        lnodes.append( self.expr() )
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def add_expr(self):
        root, lnodes = None, []
        lnodes.append( self.term() )
        while self.LA(1) == self.input.PLUS or self.LA(1) == self.input.DASH:
            temp = root
            root = self.add_op()
            root.name = "add_op"
            if temp: root.addChild(temp) 
            lnodes.append( self.term() )
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def term(self):
        root, lnodes = None, []
        lnodes.append( self.atom() )
        while self.LA(1) == self.input.STAR or self.LA(1) == self.input.FSLASH:
            temp = root
            root = self.mult_op()
            root.name = "mult_op"
            if temp: root.addChild(temp) 
            lnodes.append( self.atom() )
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def atom(self):
        root, lnodes = None, []
        if self.LA(1) == self.input.NAME:
            temp = root
            root = self.match(self.input.NAME)
            root.name = "NAME"
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.NUMBER:
            temp = root
            root = self.match(self.input.NUMBER)
            root.name = "NUMBER"
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.STRING:
            temp = root
            root = self.match(self.input.STRING)
            root.name = "STRING"
            if temp: root.addChild(temp) 
        elif  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN) :
            temp = root
            root = self.funccall()
            root.name = "funccall"
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.NAME:
            temp = root
            root = self.dotexpr()
            root.name = "dotexpr"
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.TRUE:
            temp = root
            root = self.match('True')
            root.name = "'True'"
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.FALSE:
            temp = root
            root = self.match('False')
            root.name = "'False'"
            if temp: root.addChild(temp) 
        else: raise Exception(f"Expecting something; found {self.LT(1)} on Line {self.LT(1)._line_number}.")
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def test(self):
        root, lnodes = None, []
        self.match('(')
        root = self.boolexpr()
        root.name = "boolexpr"
        self.match(')')
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def boolexpr(self):
        root, lnodes = None, []
        lnodes.append( self.and_expr() )
        while self.LA(1) == self.input.OR:
            temp = root
            root = self.match('or')
            root.name = "'or'"
            if temp: root.addChild(temp) 
            lnodes.append( self.and_expr() )
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def and_expr(self):
        root, lnodes = None, []
        lnodes.append( self.comp_expr() )
        while self.LA(1) == self.input.AND:
            temp = root
            root = self.match('and')
            root.name = "'and'"
            if temp: root.addChild(temp) 
            lnodes.append( self.comp_expr() )
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def comp_expr(self):
        root, lnodes = None, []
        lnodes.append( self.expr() )
        if self.LA(1) == self.input.DEQUALS or self.LA(1) == self.input.GE or self.LA(1) == self.input.LE or self.LA(1) == self.input.GT or self.LA(1) == self.input.LT:
            root = self.cmp_op()
            root.name = "cmp_op"
        if self.LA(1) == self.input.LPAREN or self.LA(1) == self.input.NAME or self.LA(1) == self.input.NUMBER or self.LA(1) == self.input.STRING or  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN)  or self.LA(1) == self.input.NAME or self.LA(1) == self.input.TRUE or self.LA(1) == self.input.FALSE or self.LA(1) == self.input.DASH or self.LA(1) == self.input.BANG:
            lnodes.append( self.expr() )
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def dotexpr(self):
        root, lnodes = None, []
        lnodes.append( self.match(self.input.NAME) )
        root = self.match('.')
        root.name = "'.'"
        if self.LA(1) == self.input.NAME:
            lnodes.append( self.match(self.input.NAME) )
        elif  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN) :
            lnodes.append( self.funccall() )
        else: raise Exception(f"Expecting something; found {self.LT(1)} on Line {self.LT(1)._line_number}.")
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def funcdef(self):
        root, lnodes = None, []
        root = AST(name='FUNCDEF', artificial=True)
        root.name = "$FUNCDEF"
        self.match('def')
        lnodes.append( self.match(self.input.NAME) )
        self.match('(')
        if self.LA(1) == self.input.NAME:
            lnodes.append( self.namelist() )
        self.match(')')
        lnodes.append( self.blockstat() )
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def funccall(self):
        root, lnodes = None, []
        root = self.match(self.input.NAME)
        root.name = "NAME"
        self.match('(')
        if self.LA(1) == self.input.LPAREN or self.LA(1) == self.input.NAME or self.LA(1) == self.input.NUMBER or self.LA(1) == self.input.STRING or  (self.LA(1) == self.input.NAME and self.LA(2) == self.input.LPAREN)  or self.LA(1) == self.input.NAME or self.LA(1) == self.input.TRUE or self.LA(1) == self.input.FALSE or self.LA(1) == self.input.DASH or self.LA(1) == self.input.BANG:
            lnodes.append( self.exprlist() )
        self.match(')')
        self.match(';')
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def exprlist(self):
        root, lnodes = None, []
        root = AST(name='EXPRLIST', artificial=True)
        root.name = "$EXPRLIST"
        lnodes.append( self.expr() )
        while self.LA(1) == self.input.COMMA:
            self.match(',')
            lnodes.append( self.expr() )
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def namelist(self):
        root, lnodes = None, []
        root = AST(name='NAMELIST', artificial=True)
        root.name = "$NAMELIST"
        lnodes.append( self.match(self.input.NAME) )
        while self.LA(1) == self.input.COMMA:
            self.match(',')
            lnodes.append( self.match(self.input.NAME) )
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def cmp_op(self):
        root, lnodes = None, []
        if self.LA(1) == self.input.DEQUALS:
            temp = root
            root = self.match('==')
            root.name = "'=='"
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.GE:
            temp = root
            root = self.match('>=')
            root.name = "'>='"
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.LE:
            temp = root
            root = self.match('<=')
            root.name = "'<='"
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.GT:
            temp = root
            root = self.match('>')
            root.name = "'>'"
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.LT:
            temp = root
            root = self.match('<')
            root.name = "'<'"
            if temp: root.addChild(temp) 
        else: raise Exception(f"Expecting something; found {self.LT(1)} on Line {self.LT(1)._line_number}.")
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def add_op(self):
        root, lnodes = None, []
        if self.LA(1) == self.input.PLUS:
            temp = root
            root = self.match('+')
            root.name = "'+'"
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.DASH:
            temp = root
            root = self.match('-')
            root.name = "'-'"
            if temp: root.addChild(temp) 
        else: raise Exception(f"Expecting something; found {self.LT(1)} on Line {self.LT(1)._line_number}.")
        if root:
            root.children.extend(lnodes)
            return root
        else: return lnodes[0]
    
    def mult_op(self):
        root, lnodes = None, []
        if self.LA(1) == self.input.STAR:
            temp = root
            root = self.match('*')
            root.name = "'*'"
            if temp: root.addChild(temp) 
        elif self.LA(1) == self.input.FSLASH:
            temp = root
            root = self.match('/')
            root.name = "'/'"
            if temp: root.addChild(temp) 
        else: raise Exception(f"Expecting something; found {self.LT(1)} on Line {self.LT(1)._line_number}.")
        if root:
            root.children.extend(lnodes)
            return root
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
