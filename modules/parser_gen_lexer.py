""" 
    This module contains a lexer used by parser_generator.py.
"""
import re 

class Token:
    def __init__(self, ttype: int, text: str, tname: str, line_num, char_pos, definition=None):
        """ 
            ttype : The TYPE the token should be as an int
            text  : The ACTUAL text of the token. Like ')' or 'print'
            tname : The name of the token type as a string 
        """
        self._tname = tname     # Token type as a string
        self._type = ttype      # Token type as an int
        self._text = text       # The actual token text
        self._definition = definition # For tokens like NAME where NAME can be: a - z or A - Z one or more times

        self._line_number = line_num
        self._char_position = char_pos
    
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

    def __init__(self, input: str, fpath: str):
        self.input = input              # Duh
        self.p = 0                      # Position in the input string
        self.c = self.input[self.p]     # Current char under pointed at by 'p'

        self.tokenNames = ["n/a","<EOF>",] # All token_type names as strings in a list

        # # Maps each predefined char "token" string to it's respective token type.
        # # Used by nextToken() to lex said token strings. 
        self.char_to_ttype = {} 

        # Read in token definitions from file:
        # ---------------------------------------------------------------------
        token_defs = self.read_tokens(fpath)

        self.line_num = 0    # Used when syntax errors arise to return problem char location to user 
        self.char_pos = 0

        self.keywords = {}

        self.multi_char_lexers = []

        # For debug purposes:
        self.token_list = []

        # Build out attributes, a list of token names, and a  
        # dict of char to token name from the symbols dict:
        # ---------------------------------------------------------------------
        for i, name in enumerate(token_defs, start=2):        
            defn = token_defs[name]
            self.__setattr__(name,i)        # Set instance field            
            self.tokenNames.append(name)    # Add token_name to list of token names
            if defn[0:3] != 're':          # Add char:token_name pairing to dict 
                defn = defn[1:-1]           # Remove quotes to avoid double quoting 
                self.char_to_ttype[defn] = i  

            # Generate lexing info sets for NON_PRE_DEF tokens like STRING or NAME
            # For those cases, 'text' will be the root of a Node tree 
            if defn[0:3] == 're' or len(defn) > 1: 
                start_set = 0 # some range (same as char_set for NPD)
                char_set  = 0 
                multi_char_type = "NON_PRE_DEF"

                if type(defn) is str:  # PRE_DEF                    
                    start_set = defn[0]
                    char_set  = defn 
                    multi_char_type = "PRE_DEF"
                    self.keywords[defn] = 1

                elif type(defn) is Node: 
                    # Compute the start_set for each Non-predefined token:               
                    start_set = self.compute_char_set(defn.nodes[0])
                    if len(defn.nodes)==1: pass
                    char_set = defn 
                        
                
                token_name = name                 

                self.multi_char_lexers.append((start_set, 
                                                char_set, 
                                                token_name, 
                                                multi_char_type))

    def read_tokens(self, fpath):
        lines = []
        with open(fpath) as f: 
            # Get to the token portion of the grammar file:
            while "TOKENS" not in f.readline(): pass
            # Get token lines:
            while "END" not in (line := f.readline()): 
                if line[0] == '#' or len(line.rstrip('\n')) == 0: continue
                lines.append(line)

        token_defs = {}
        for line in lines: 
            lexical_tkns = line.split()            
            k,v = lexical_tkns[0:2]
            token_defs[k] = v
        return token_defs

    def _strip_quotes(self, name):
        """" Strips single quotes on both sides of a string if present"""
        if len(name) >= 3 and name[0] == r"'" and name[-1] == r"'":
            return name[1:-1]
        return name 

    def consume(self):
        """ Increments the char pointer int 'p' by one and sets 
            'c' to the next char in the input string """
        self.p += 1
        if self.p >= len(self.input):
            self.c = self.EOF 
        else: 
            self.c = self.input[self.p]

            self.char_pos += 1
            
            if self.c == '\n': 
                self.char_pos = 0
                self.line_num += 1 
    
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
        """ Returns the name of a token type given token type as an int.
        
            Example: getTokenName(0)    ->    returns "NAME" 
        """
        return self.tokenNames[token_type]
    
    def getTokenType(self, token_text: str) -> int:
        """ Returns the token type as an int of a token given text of the token.
            
            Example: getTokenType('}')      ->  returns < an int > 
        """
        return self.char_to_ttype[token_text]

    def getTokenNameFromText(self, token_text: str)  -> str:
        """ Returns the token name as a string for a given token text string.
            
            Example: getTokenNameFromText('print')   ->   returns "PRINT" 

            This method is ultimately checking self.char_to_ttype for the item,
            if it isn't in it, it will return "NOT_A_TOKEN"
        """
        if token_text.isupper(): return token_text
        if token_text not in self.char_to_ttype: return "NOT_A_TOKEN"
        return self.getTokenName( self.getTokenType(token_text) )

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
                raise Exception(f"Invalid character: {self.c} on line {self.line_num}, position {self.char_pos}")
        else:
            while char_selector(self.c):
                multichar += self.c
                self.consume()
        
        # Check if multichar is a keyword token: If so, override token_type
        if multichar in self.keywords: token_type = self.getTokenType(multichar)
        # -------------------------------------------------------------
        return Token(token_type, multichar, self.getTokenName(token_type), self.line_num, self.char_pos)

    def _WS(self):
        """ Consumes whitespace until a non-whitespace char is encountered. """
        while self.c in [' ','\t','\n','\r']: self.consume()
    
    def _comment(self):
        """ Skips comments, lines that start with a '#', by consuming chars until a new line is encountered. """
        while self.c != '\n': 
            self.consume()      # Consume the comment,         

    def nextToken(self) -> Token:
        """ Returns the next char in the input string. 
            If there is no next char, returns <EOF> (End of File) """
        while self.c != Lexer.EOF: 
            # Handle Whitespace:
            # ----------------------------------------
            if self.c in [' ','\t','\n','\r']: 
                self._WS() 
                continue 
            
            # Skip comments: 
            # ---------------------------------------
            if self.c == '#': 
                self._comment()
                continue
              
            # Handle any multi-character token, and some single char tokens:
            # -----------------------------------------------------------------

            for start_set, char_set, t_name, multi_char_type in self.multi_char_lexers:
                # Start_set is one char for Pre-defined multic_char tokens
                #      ...  is a function which checks if the char is a member for Non-Pre-Defined ... 

                # Skip the body unless we have self.c == a start character (or be a member of a given char set)
                if   multi_char_type == "PRE_DEF"     and self.c != start_set:   continue
                elif multi_char_type == "NON_PRE_DEF" and type(start_set) == set and self.c not in start_set: 
                    continue
                
                multi_char = ""

                if multi_char_type == "PRE_DEF":  
                    for i,c in enumerate(char_set, start=1):
                        if self.c != c: break
                        multi_char += c
                        self.consume()                    
                    else:
                        ttype = self.char_to_ttype[multi_char]
                        return Token(ttype, multi_char, self.getTokenName(ttype), self.line_num, self.char_pos)

                    # Check if we lexed a single char token:
                    if len(multi_char) == 1 and multi_char in self.char_to_ttype:
                        ttype = self.char_to_ttype[multi_char]
                        return Token(ttype, multi_char, self.getTokenName(ttype), self.line_num, self.char_pos)

                    # If not that, rewind the char stream. We might have started to lex
                    # 'else' when we were actually trying to lex 'elif'. In that case we would 
                    # rewind by 2 chars and try lexing again:
                    elif len(multi_char) > 0:                      
                        self.rewind(i)
                    
               
            # Handle single character tokens:
            # ----------------------------------------
            for c,ttype in self.char_to_ttype.items():
                if self.c == c and ttype != "NON_PRE_DEF": 
                    self.consume()
                    tkn = Token(ttype, c, self.getTokenName(ttype), self.line_num, self.char_pos)
                    #print(tkn)
                    return tkn

            # If self.c matched no valid character then: 
            raise Exception(f"Invalid character: < {self.c}; ord: {ord(self.c)} > on line {self.line_num}, position {self.char_pos}")

        
        new_token = Token(self.EOF_TYPE, "<EOF>", self.getTokenName(self.EOF_TYPE), self.line_num, self.char_pos)
        return new_token

            
if __name__ == "__main__":
    input = \
"""
x=0;
print("Hello world");
if(x >= 120){
    print("xis0");
    x=1;

#cmt

    if ( x == 0 ) print("Aww yeah");    
}
"""
    import os; cwd = os.getcwd()[:-8]

    #lexer = Lexer(input, cwd + "\\grammar_grammar.txt" ) 
    lexer = Lexer(input, cwd + "\\docs\\DrewGrammar.txt" ) 
    #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    #print("DLexer Class after initialization:")
    #for k,v in lexer.__dict__.items(): print(f"{k}\t: {v}")

    t = lexer.nextToken()
    lexer.token_list.append(t)
    i = 0
    while t._type != lexer.EOF_TYPE:
        print(i, '\t', t)
        t = lexer.nextToken()
        lexer.token_list.append(t)
        i+=1
    print(t)
    print()