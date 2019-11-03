""" This module contains a user configurable lexer.

    In order to use this lexer module:
    
    * Create a newline seperated list of symbols in a file:
        > <TOKEN_NAME>    <token_char> # Format
        > COMMA         ,              # Example

        > For any multi char tokens:
            > <TOKEN_NAME>    multi # Format        
            > NAME            multi # Example

    * For any multi char tokens: 
        > Implement a function:
            * A recognizer  -> Recognizes the start symbol of a given token

        > Put NAME, recognizer, and Builder in a tuple list:
            * multi_char_recogs = [ (NAME,recog), etc etc ]

    The lexer will automatically create fields for every token name in the file.
    The lexer will use the provided recognizer function to lex multi char tokens.

    For an example, see the d_lexer module.

    You do not have to do the above actions in a class, but I recommend doing so. 

    My recommendation: 
        1.  Create a class which inherits from Lexer
        2.  In your __init__() function, setup the prescribed above actions and 
            then call super().__init__(...) 

        Ex: 
            class DLexer(Lexer): 
                # Read in token definitions from file:
                fpath="token_defs.txt"
                token_defs = { l.split()[0]:l.split()[1] for l in open(fpath).readlines() }

                # Functions to configure the lexer
                isLetter = lambda c: (c>= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z')
                isDigit  = lambda c: c >= '0' and c <= '9'
                multi_char_recognizers = [ ("NAME", isLetter), ("NUMBER", isDigit) ]    
                
                super().__init__(input, token_defs, multi_char_recognizers)        
 """
class Token:
    def __init__(self, ttype, text, tname):
        self._tname = tname     # Token type as a string
        self._type = ttype      # Token type as an int
        self._text = text       # The actual token text
    
    def __str__(self): return f"<'{self._text}', {self._tname}>"

class Lexer:
    
    EOF = chr(0)        # Represent EOF char
    EOF_TYPE = 1        # Represent EOF Token type

    def __init__(self, input, fpath, multi_char_recognizers):
        self.input = input              # Duh
        self.p = 0                      # Position in the input string
        self.c = self.input[self.p]     # Current char under pointed at by 'p'

        self.tokenNames = ["n/a", "<EOF>",] # All token_type names as strings in a list

        # # Maps each singular char "token" string to it's respective token type.
        # # Used by nextToken() to lex said token strings. 
        self.char_to_ttype = {} 

        # Read in token definitions from file:
        token_defs = { l.split()[0]:l.split()[1] for l in open(fpath).readlines() }

        # Build out attributes, a list of token names, and a  
        # dict of char to token name from the symbols dict:
        for name, i in zip(token_defs, range( 2, len(token_defs) + 2) ):
            char = token_defs[name]
            self.__setattr__(name,i)        # Set instance field
            self.tokenNames.append(name)    # Add token_name to list of token names
            if char != 'multi': 
                self.char_to_ttype[char] = i # Add char:token_name pairing to dict (Only for single char tokens)
            
        self.multi_char_recognizers = multi_char_recognizers # See nextToken() for what this is

    def consume(self):
        """ Increments the char pointer int 'p' by one and sets 
            'c' to the next char in the input string """
        self.p += 1
        if self.p >= len(self.input):
            self.c = self.EOF 
        else: 
            self.c = self.input[self.p]
        
    def match(self, x):
        if self.c == x: 
            self.consume()
        else: 
            raise Exception(f"Expecting {x}; found {self.c}")

    def getTokenName(self, x): 
        return self.tokenNames[x]

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

    def _WS(self):
        """ Consumes whitespace until a non-whitespace char is encountered. """
        while self.c in [' ','\t','\n','\r']: self.consume()

    def nextToken(self):
        """ Returns the next char in the input string. 
            If there is no next char, returns <EOF> (End of File) """
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

            
          