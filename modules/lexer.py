""" This module contains a user configurable lexer.

    
    NOTE: Some of this is out of date, some of it is flat out not true anymore.
    TODO: Update this doc


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

from parser_generator import GrammarReader, Node, RuleToken

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
        reader = GrammarReader()
        token_defs = reader.read_tokens(fpath)

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
            if type(defn) != Node:          # Add char:token_name pairing to dict 
                defn = defn[1:-1]           # Remove quotes to avoid double quoting 
                self.char_to_ttype[defn] = i  

            # Add all info to multi_char_lexers: 
            if False and type(defn) == Node or (type(defn) != Node and len(defn) > 1):
                start_set = 0 # some range (same as char_set for NPD)
                char_set  = 0 
                multi_char_type = "NON_PRE_DEF"
                
                # TEMPORARY Until I implement a way to generate these from the grammar file:
                # ---------------------------------------------------------------------
                if name == "NAME": 
                    start_set = lambda c: (c>= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z')
                    char_set  = start_set

                if name == "NUMBER":
                    start_set = lambda c: c >= '0' and c <= '9'
                    char_set = start_set
                
                if name == "STRING":
                    start_set = lambda c: c == '"'  # For DrewLang 
                    #start_set = lambda c: c == "'" # For grammar grammar 
                    char_set  = lambda c: c != '"'  # Want to make BOTH work at some point
                    #char_set  = lambda c: c != "'" # But only accept one type at a time. 
                    end_set   = start_set 


                elif type(defn) != Node: # PRE-DEF Token: 
                    start_set = defn[0]
                    char_set  = defn 
                    multi_char_type = "PRE_DEF"
                    self.keywords[defn] = 1
                
                token_name = name                 

                self.multi_char_lexers.append((start_set, char_set, token_name, multi_char_type))
            
            # Generate lexing functions for NON_PRE_DEF tokens like STRING or NAME
            # For those cases, 'text' will be the root of a Node tree 
            # 
            # NOTE: New code below: Will generate recognizers from Rule ASTs
            #
            if (type(defn) == Node or len(defn) > 1):
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

    def compute_char_set(self, defn: Node, ret_set=None) -> set:
        if ret_set is None: ret_set = set()
     
        if defn.type == RuleToken.TERMINAL: return set(self._strip_quotes(defn.name))

        if defn.name == '..': # Range operator:
            start = self._strip_quotes(defn.nodes[0].name) # Get limits of this range
            end   = self._strip_quotes(defn.nodes[1].name)
            
            # Generate all chars in the range
            return set( chr(i) for i in range(ord(start), ord(end)+1) )                        

        if defn.type in [RuleToken.MODIFIER, RuleToken.SUB_RULE] or defn.name == "BLANK":
            for node in defn.nodes:
                ret_set.update(
                    self.compute_char_set(node, ret_set=ret_set)
                ) 
            return ret_set
        return ret_set

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
        self.consume()          # Consume the new line 

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
            if self.c == '#': self._comment()
              
            # Handle any multi-character token, and some single char tokens:
            # -----------------------------------------------------------------

            for start_set, char_set, t_name, multi_char_type in self.multi_char_lexers:
                # Start_set is one char for Pre-defined multic_char tokens
                #      ...  is a function which checks if the char is a member for Non-Pre-Defined ... 

                # Skip the body unless we have self.c == a start character (or be a member of a given char set)
                if   multi_char_type == "PRE_DEF"     and self.c != start_set:   continue
                elif multi_char_type == "NON_PRE_DEF" and type(start_set) == set and self.c in start_set: continue

                multi_char = self.c
                self.consume()

                if multi_char_type == "PRE_DEF":        
                    char_set = char_set[1:] # Remove first char since it's already in multi_char                                 
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
                    
                elif multi_char_type == "NON_PRE_DEF": 
                    def temp_func_name(node, multi_char, chars_consumed=0): 
                        """ Change name of func to something that makes sense"""
                        if node.name == '.': # Match any char:
                            multi_char += self.c 
                            self.consume()
                            chars_consumed += 1
                            return multi_char, chars_consumed

                        if node.name == '*':
                            char_set = self.compute_char_set(node.nodes[0])
                            loop = lambda n: n in char_set
                            if len(node.nodes) == 2:
                                loop = lambda n: n != node.nodes[1]

                            while loop(self.c):
                                multi_char += self.c 
                                self.consume()
                                chars_consumed += 1

                                # NOTE: RESUME HERE 

                    escape_next = False

                    root = char_set # Root of our lexical rule tree is char_set

                    for node in root.nodes: 
                        temp_func_name(node)
                    
                    ttype = getattr(self, t_name)
                    return Token(ttype, multi_char, self.getTokenName(ttype), self.line_num, self.char_pos )

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
if(x >= 0){
    print("xis0");
    x=1;

    if ( x == 0 ) print("Fuck yeah");
}
"""
    #lexer = Lexer(input, "C:\\Users\\Drew\\Desktop\\Code Projects\\DrewLangPlayground\\DrewLang\\grammar_grammar.txt" ) 
    lexer = Lexer(input, "C:\\Users\\Drew\\Desktop\\Code Projects\\DrewLangPlayground\\DrewLang\\DrewGrammar.txt" ) 
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