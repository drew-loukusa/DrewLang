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
    def __init__(self, ttype: int, text: str, tname: str):
        """ 
            ttype : The TYPE the token should be as an int
            text  : The ACTUAL text of the token. Like ')' or 'print'
            tname : The name of the token type as a string 
        """
        self._tname = tname     # Token type as a string
        self._type = ttype      # Token type as an int
        self._text = text       # The actual token text
    
    def __str__(self): return f"<'{self._text}', {self._tname}>"

class Lexer:
    
    EOF = chr(0)        # Represent EOF char
    EOF_TYPE = 1        # Represent EOF Token type


    # TODO: Make the lexer accept a list of tuples
    #       Each tuple is THREE funcs: 
    #                                   start_of_sequence, 
    #                                   member_of_body,
    #                                   end_of_sequence
    #       For multi-char token parsing
    #       Not every multi char token uses end_of_sequence

    def __init__(self, input: str, fpath: str, multi_char_recognizers: list, visitors=None):
        self.input = input              # Duh
        self.p = 0                      # Position in the input string
        self.c = self.input[self.p]     # Current char under pointed at by 'p'

        self.tokenNames = ["n/a","<EOF>",] # All token_type names as strings in a list

        # # Maps each singular char "token" string to it's respective token type.
        # # Used by nextToken() to lex said token strings. 
        self.char_to_ttype = {} 

        # Read in token definitions from file:
        lines = []
        with open(fpath) as f: 
            # Get to the token portion of the grammar file:
            while "TOKENS" not in f.readline(): pass
            # Get token lines:
            while "END" not in (line := f.readline()): lines.append(line)
        token_defs = { l.split()[0]:l.split()[1] for l in lines }

        self.keywords = {}

        # Build out attributes, a list of token names, and a  
        # dict of char to token name from the symbols dict:
        for name, i in zip(token_defs, range( 2, len(token_defs) + 2) ):
            text = token_defs[name]
            self.__setattr__(name,i)        # Set instance field
            self.tokenNames.append(name)    # Add token_name to list of token names
            self.char_to_ttype[text] = i    # Add char:token_name pairing to dict 

            # If token is a keyword, add it to our keyword dict:
            if len(text) > 1 and text != "multi": self.keywords[text] = 1
            
        self.multi_char_recognizers = multi_char_recognizers # See nextToken() for what this is


        # Visitors is a list of tuples: 
        # ( Start_of_sequence_character, build_token_function )
        self.visitors = visitors if visitors is not None else []
        
    def consume(self):
        """ Increments the char pointer int 'p' by one and sets 
            'c' to the next char in the input string """
        self.p += 1
        if self.p >= len(self.input):
            self.c = self.EOF 
        else: 
            self.c = self.input[self.p]
    
    def rewind(self, n: int):
        """ Rewinds the character stream by 'n' characters. 
            Sets self.p = self.p - n
            Then, sets self.c = self.p  """
        self.p = self.p - n 
        self.c = self.input[self.p]

    def match(self, token_type: int):
        if self.c == token_type: 
            self.consume()
        else: 
            raise Exception(f"Expecting {token_type}; found {self.c}")

    def getTokenName(self, token_type: int) -> str:
        return self.tokenNames[token_type]
    
    def getTokenType(self, token_name: str) -> int:
        return self.char_to_ttype[token_name]

    # TODO: Make VV accept an "end of sequence" function 
    #       while char_selector(self.c) and not end_of_sequence(self.c):
    #       
    def parseMultiChar(self, token_type: int, char_selector, end_of_seq=None) -> Token:
        """ Used to parse multi char tokens. 
            * char_selector: Function for recognizing a given char
            * token_type: The type the returned token should be.
            
            @Return: A Token of type 'token_type' """
        multichar = self.c
        self.consume()
        if end_of_seq:
            while char_selector(self.c):
                multichar += self.c
                self.consume()
            if end_of_seq(self.c):
                multichar += self.c
                self.consume()
            else: 
                raise Exception(f"Invalid character: {self.c}")
        else:
            while char_selector(self.c):
                    multichar += self.c
                    self.consume()
        
        # Check if multichar is a keyword token: If so, override token_type
        if multichar in self.keywords: token_type = self.getTokenType(multichar)
        # -------------------------------------------------------------
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


            # NOTE: Experimential Changes:
            # I'm going to experirment with passing in external functions that I then
            # pass self.consume() and self.c() or self ? 

            # Point is, the external funcs will have the ability to move the pointed at char
            # and call consume()

            # tHis will allow the lexer to match arbitrary char sequences 
            # Each external func will have a Start-of-sequence recognizer 
            # We call teh visitor if the S.O.Q returns true, but we don't do anything
            # if the visitor fails to build a token: The token could possibly be something else.

            # this will probably require a the ability to rewind the chararcter stream OHH
            # This is getting into parsing territory, but I'm going to see how it goes.
        
            # I think rewinding just consists of resetting self.p to where it was before calling
            # the visiting function and resetting self.c to whatever is at self.p. <-- nailed it

            # might even want to create a func for that.
            # Have each visitor func, if it does not return a token, return how many chars it recognized
            # then we can rewind the char stream by that much.

            # Like: 
            # if recognizer_for_visitor(self.c):
            #       token_maybe = visitor(self)  #pass in self instance to allow visitor to call consume
            #       if token_maybe is not token: self.rewind_chars(token_maybe) 
            for token_name, c, build_token_func in self.visitors:
                if self.c == c: 
                    string_or_int = build_token_func(self)
                    if type(string_or_int) is str: 
                        ttype = getattr(self, token_name)
                        tname = self.getTokenName(ttype)
                        return Token(ttype, string_or_int, tname)
                    else: # if string_or_int is int: 
                        self.rewind(string_or_int)

            # Temp code:
             # You could use this to lex keywords... I have a method already but...
             # I have a thing in parseMultiChar that handles them. I'm not sure if I like it, 
             # so Maybe I'll switch to this. The advatage to the other way is no re-winding.
            
            # This could allow for NON-alphanumeric chars tho:

            if False:
                keywords = [(1,2),(2,3)]
                n = 0
                for token_name, keyword in keywords:
                    if keyword[0] != self.c: continue                    
                    multi_char = self.c
                    self.consume()
                    for c in keyword:
                        if c == self.c:
                            multi_char += self.c
                        else:
                            self.rewind(n)
                            break
            
            # More temp code to figure out how I'm going to handle set based tokens 
            # TODO: Work on this if I feel like it. 
            # I'm going stop working on this to go get my AST implemented k?
            if False:
                foobar = [(1,2,3)]
                for token_name, start_char, descrip in foobar: 
                    pass

            # Handle multi character tokens:
            # ----------------------------------------
            # > Iterate through the list of functions passed in on instance creation.
            # > Use those to recognize the possible start of a multi char token.
            # > If a recognizer returns true, parse and return the token:
            for name,recognizer_set in self.multi_char_recognizers:
                start_of_seq, body_memb, end_of_seq = recognizer_set
                if start_of_seq(self.c): 
                    tkn = self.parseMultiChar(getattr(self, name), body_memb, end_of_seq)        
                    #print(tkn)
                    return tkn

            # Handle single character tokens:
            # ----------------------------------------
            for c,ttype in self.char_to_ttype.items():
                if self.c == c and ttype != "multi": 
                    self.consume()
                    tkn = Token(ttype, c, self.getTokenName(ttype))
                    #print(tkn)
                    return tkn

            # If self.c matched no valid character then: 
            raise Exception(f"Invalid character: {self.c}")
        
        return Token(self.EOF_TYPE, "<EOF>", self.getTokenName(self.EOF_TYPE))

            
          