
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

    def toStringTree(self):
        if len(self.children) == 0: return self.toString()

        buf = ""
        if not self.isNone(): 
            buf += f"({self.toString()} "
        
        for child in self.children:
            if child != self.children[0]: 
                buf += " "
            buf += child.toStringTree()
            
        if not self.isNone():
            buf += ')'
        
        return buf