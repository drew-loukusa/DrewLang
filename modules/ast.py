
from lexer import Token

class AST:

    def __init__(self, token=None, token_type=None, token_text=None, token_name=None, artificial=False, name=None):
        self.artificial = artificial
        self.name = name
        self.token = token  # From which token did we create node?
        self.children = []  # normalized list of AST nodes

        if token_type: self.token = Token(token_type, token_text, token_name)

    def isNone(self): return self.token is None 

    def addChild(self, t): self.children.append(t)

    def toString(self):
        return str(self.token) if self.token is not None else "None"

    def toStringTree(self, tab=0):
        if len(self.children) == 0: 
            print('--'*tab + self.toString())
            return

        if not self.isNone(): 
            print('--'*tab + f"{self.toString()}")
        
        for child in self.children:
            child.toStringTree(tab+1)
        
        #return buf