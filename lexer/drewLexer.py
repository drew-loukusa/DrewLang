from lexer import Lexer 

class Token:
    def __init__(self, ttype, text, tname):
        self._tname = tname     # Token type as a string
        self._type = ttype      # Token type as an int
        self._text = text       # The actual token text
    
    def __str__(self): return f"<'{self._text}', {self._tname}>"

class DLexer(Lexer):
  
    def __init__(self, input, symbols, multi_char_recognizers):
        super().__init__(input)
  
        self.tokenNames = ["n/a", "<EOF>",]

        # # Maps each singular char "token" string to it's respective token type.
        # # Used by nextToken() to lex said token strings. 
        self.char_to_ttype = {}

        # Build out attributes, a list of token names, and a  
        # dict of char to token name from the symbols dict:
        for name, i in zip(symbols, range( 2, len(symbols) + 2) ):
            char = symbols[name]
            self.__setattr__(name,i)        # Set instance field
            self.tokenNames.append(name)    # Add token_name to list of token names
            if char != 'multi': 
                self.char_to_ttype[char] = i # Add char:token_name pairing to dict (Only for single char tokens)
            
        self.multi_char_recognizers = multi_char_recognizers

    def getTokenName(self, x): 
        return self.tokenNames[x]

    def isLetter(self): 
        return (self.c>= 'a' and self.c <= 'z') or (self.c >= 'A' and self.c <= 'Z') 

    def isDigit(self): 
        return self.c >= '0' and self.c <= '9'
    
    def parseMultiChar(self, char_selector, token_type):
        """ Used to parse multi char tokens. 
            * char_selector: Function for recognizing a given char
            * token_type: The type the returned token should be.
            
            @Return: A Token of type 'token_type' """
        multichar = self.c
        self.consume()
        while char_selector(self.c):
            multichar += self.c
            self.consume()
        return Token(token_type, multichar, self.getTokenName(token_type))

    #def _NAME(self): return self.__parseMultiChar(self.isLetter, self.NAME)

    #def _NUMBER(self): return self.__parseMultiChar(self.isDigit, self.NUMBER)

    def _WS(self):
        while self.c in [' ','\t','\n','\r']: self.consume()

    def nextToken(self):
        while self.c != Lexer.EOF: 
            # Handle Whitespace:
            # ----------------------------------------
            if self.c in [' ','\t','\n','\r']: 
                self._WS() 
                continue 

            # Handle multi character tokens:
            # ----------------------------------------
            # > Iterate through the list of functions passed in on instance creation.
            # > Use those to recognize the possible start of a multi char token.
            # > If a recognizer returns true, parse and return the token:
            for name,recognizer in self.multi_char_recognizers:
                if recognizer(self.c): 
                    return self.parseMultiChar(recognizer, getattr(self, name))        

            # Handle single character tokens:
            # ----------------------------------------
            for c,ttype in self.char_to_ttype.items():
                if self.c == c: 
                    self.consume()
                    return Token(ttype, c, self.getTokenName(ttype))

            # If self.c matched no valid character then: 
            raise Exception(f"Invalid character: {self.c}")
        
        return Token(self.EOF_TYPE, "<EOF>", self.getTokenName(self.EOF_TYPE))

            
          