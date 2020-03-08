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
        self.token_defs = {} ; self._read_tokens(fpath)

        self.line_num = 0    # Used when syntax errors arise to return problem char location to user 
        self.char_pos = 0

        self.keywords = {}

        self.multi_char_lexers = []

        # For debug purposes:
        self.token_list = []

        # Build out attributes, a list of token names, and a  
        # dict of char to token name from the symbols dict:
        # ---------------------------------------------------------------------
        self._generate_attrs_and_fill_class_data()
      
    def _generate_attrs_and_fill_class_data(self):
        for i, name in enumerate(self.token_defs, start=2):        
            defn = self.token_defs[name]
            self.__setattr__(name,i)        # Set instance field            
            self.tokenNames.append(name)    # Add token_name to list of token names
            if defn[0][0:2] != 're':          # Add char:token_name pairing to dict 
                defn = defn[1:-1]           # Remove quotes to avoid double quoting 
                self.char_to_ttype[defn] = i  

            # Generate lexing info sets for NON_PRE_DEF tokens like STRING or NAME
            # For those cases, 'char_set' will be a regex

            # for PRE_DEF: char_set == string
            # NON_PRE_DEF: char_set == regex pattern object

            if defn[0][0:2] == 're' or len(defn[0]) > 1: 
                start_set = 0 # some range (same as char_set for NPD)
                char_set  = 0 
                multi_char_type = "NON_PRE_DEF"

                if defn[0][0:2] == 're': # NON_PRE_DEF 
                    pattern = defn[0][3:]
                    start_set = defn[1] 

                    if '..' in start_set: 
                        start, end = start_set[0], start_set[3]
                        start_set = set( chr(i) for i in range(ord(start), ord(end)+1) ) 
                    else:
                        start_set = set(defn[1])
                    
                    char_set = re.compile(pattern=pattern)

                else:  # PRE_DEF                    
                    start_set = set(defn[0][0])
                    char_set  = defn[0]
                    multi_char_type = "PRE_DEF"
                    self.keywords[defn] = 1

                token_name = name                 

                self.multi_char_lexers.append(
                                                (
                                                start_set, 
                                                char_set, 
                                                token_name, 
                                                multi_char_type,
                                                )
                                            )

    def _read_tokens(self, fpath):
        """ Accepts path to file containing token definitions.
            Returns: Nothing but...

            Fills in self.token_defs with: 
                
                A dictionary of token_name -> definiton_list 

            definition_list : Is usually a list of length 1 containing the actual token text as a string

            For single char tokens and pre-defined multi char tokens (like 'while') this will be the case.

            For non-pre-defined multi-char tokens, like NAME ( A to Z, one or more times), the list will 
            contain the following items:

                A regex describing the token as a string ; The start set of the token as a string

            The regex string will look like this: "re(<regex_string>)" 
            The start set might look like this: "A..Z" (A to Z) or be a singe char
        """
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
            k,v = lexical_tkns[0], lexical_tkns[1:]
            token_defs[k] = v
        
        self.token_defs = token_defs

    def _strip_quotes(self, name):
        """" Strips single quotes on both sides of a string if present"""
        if len(name) >= 3 and name[0] == r"'" and name[-1] == r"'":
            return name[1:-1]
        return name 

    def _consume(self):
        """ Increments the char pointer int 'p' by one and sets 
            'c' to the next char in the input string 
            
            Also returns the NEW char pointed at by new 'p' """
        self.p += 1
        if self.p >= len(self.input):
            self.c = self.EOF 
        else: 
            self.c = self.input[self.p]

            self.char_pos += 1
            
            if self.c == '\n': 
                self.char_pos = 0
                self.line_num += 1 
        
        return self.c
    
    def _rewind(self, n: int):
        """ Rewinds the character stream by 'n' characters. 
            Sets self.p = self.p - n
            Then, sets self.c = self.p  """
        self.p = self.p - n 
        self.c = self.input[self.p]

    def _match(self, token_type: int):
        if self.c == token_type: 
            self._consume()
        else: 
            raise Exception(f"Expecting {token_type}; found {self.c}")

    def _getTokenName(self, token_type: int) -> str:
        """ Returns the name of a token type given token type as an int.
        
            Example: _getTokenName(0)    ->    returns "NAME" 
        """
        return self.tokenNames[token_type]
    
    def _getTokenName(self, token_text: str) -> int:
        """ Returns the token type as an int of a token given text of the token.
            
            Example: _getTokenName('}')      ->  returns < an int > 
        """
        return self.char_to_ttype[token_text]

    def _getTokenNameFromText(self, token_text: str)  -> str:
        """ Returns the token name as a string for a given token text string.
            
            Example: getTokenNameFromText('print')   ->   returns "PRINT" 

            This method is ultimately checking self.char_to_ttype for the item,
            if it isn't in it, it will return "NOT_A_TOKEN"
        """
        if token_text.isupper(): return token_text
        if token_text not in self.char_to_ttype: return "NOT_A_TOKEN"
        return self._getTokenName( self._getTokenName(token_text) )

    def _WS(self):
        """ Consumes whitespace until a non-whitespace char is encountered. """
        while self.c in [' ','\t','\n','\r']: self._consume()
    
    def _comment(self):
        """ Skips comments, lines that start with a '#', by consuming chars until a new line is encountered. """
        while self.c != '\n': 
            self._consume()      # Consume the comment,         

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
                if   multi_char_type == "PRE_DEF"     and self.c not in start_set:  continue
                elif multi_char_type == "NON_PRE_DEF" and self.c not in start_set:  continue
                
                multi_char = ""

                if multi_char_type == "PRE_DEF":  
                    for i,c in enumerate(char_set, start=1):
                        if self.c != c: break
                        multi_char += c
                        self._consume()                    
                    else:
                        ttype = self.char_to_ttype[multi_char]
                        return Token(ttype, multi_char, self._getTokenName(ttype), self.line_num, self.char_pos)

                    # Check if we lexed a single char token:
                    if len(multi_char) == 1 and multi_char in self.char_to_ttype:
                        ttype = self.char_to_ttype[multi_char]
                        return Token(ttype, multi_char, self._getTokenName(ttype), self.line_num, self.char_pos)

                    # If no tokens were sucessfully lexed, rewind the char stream if needed:
                    elif len(multi_char) > 0:                      
                        self._rewind(i)

                    # Why rewind? An example:
                    #   We may have attempted to lex the the phrase 'elif' as 'else' because
                    #   they both start with 'el'. If this happened, rewind the char stream by
                    #   2 chars and try lexing again.

                elif multi_char_type == "NON_PRE_DEF":
                    
                    # Add the first character to the multi_char:
                    multi_char += self._consume()               

                    # Using regex: 
                    # Add characters to multi_char until you have a full match
                    match = None
                    while (match := char_set.full_match(multi_char)) == None:
                        multi_char += self._consume()

                    # Then, add 1 more char, check if match: 
                    multi_char += self._consume()
                    end_check = char_set.fullmatch(multi_char)

                    # Rewind char stream by 1 if current token ended 1 char before:
                    if end_check is None: self._rewind(1)

                    # Save the most recent full match:
                    last_match = end_check if end_check != None else match 

                    # If it is a full match repeat steps 
                    if end_check is not None:                                                
                        while (match := char_set.full_match(multi_char)) != None:
                            last_match = match
                            multi_char += self._consume()                        
                        # Rewind since above loop will always go 1 char past end of current token
                        self._rewind(1) 
                        
                    # If it is not a match, stop and return the original matched string:
                    if last_match is None:
                        # Create and return a Token using 'match' 
                        pass
                    else:
                        # Create and return a Token using 'last_match'
                        pass

                    # NOTE: Using this method will allow you to return an error like:

                        # " Reached EOF while attempting to parse a STRING on line X. 
                        #   You may have forgotten a closing quote somewhere. "
                        
            # Handle single character tokens:
            # ----------------------------------------
            for c,ttype in self.char_to_ttype.items():
                if self.c == c and ttype != "NON_PRE_DEF": 
                    self._consume()
                    tkn = Token(ttype, c, self._getTokenName(ttype), self.line_num, self.char_pos)
                    #print(tkn)
                    return tkn

            # If self.c matched no valid character then: 
            raise Exception(f"Invalid character: < {self.c}; ord: {ord(self.c)} > on line {self.line_num}, position {self.char_pos}")

        
        new_token = Token(self.EOF_TYPE, "<EOF>", self._getTokenName(self.EOF_TYPE), self.line_num, self.char_pos)
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