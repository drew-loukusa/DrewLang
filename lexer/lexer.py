class Lexer:
    EOF = chr(0)        # Represent EOF char
    EOF_TYPE = 1        # Represent EOF Token type
    def __init__(self, input):
        self.input = input
        self.p = 0
        self.c = self.input[self.p]

    def consume(self):
        self.p += 1
        if self.p >= len(self.input):self.c = self.EOF 
        else: self.c = self.input[self.p]

    def match(self, x):
        if self.c == x: self.consume()
        else: raise Exception(f"Expecting {x}; found {self.c}")