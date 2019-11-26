from d_lexer import DLexer
import time

class Parser:
    def __init__(self, input, k):
        self.input = DLexer(input,"C:\\Users\\Drew\\Desktop\\Code Projects\\DrewLangPlayground\\DrewLang\\grammar_grammar.txt" ) 
        self.k = k      # How many lookahead tokens
        self.p = 0      # Circular index of next token positon to fill
        self.lookahead = [] # Circular lookahead buffer 
        for _ in range(k): # Prime buffer
            self.lookahead.append(self.input.nextToken())

    def consume(self):
        self.lookahead[self.p] = self.input.nextToken()
        self.p = (self.p+1) % self.k 

    def LT(self, i): 
        #print("Hey", i)
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
            self.consume()
        else:
            raise Exception(f"Expecting {self.input.getTokenName(x)}; found {self.LT(1)} on line # {self.LT(1)._line_number}")
    
    def grammar(self):
        while self.LA(1) == self.input.NAME:
            self.rule()
    
    def rule(self):
        self.NAME()
        self.match(':')
        while self.LA(1) == self.input.LPAREN or self.LA(1) == self.input.STRING or self.LA(1) == self.input.NAME:
            self.or_tokens()
        self.match(';')
    
    def or_tokens(self):
        self.and_tokens()
        while self.LA(1) == self.input.OR:
            self.match('|')
            self.and_tokens()
    
    def and_tokens(self):
        self.cmpd_token()
        while self.LA(1) == self.input.AND:
            self.match('&')
            self.cmpd_token()
    
    def cmpd_token(self):
        self.atom()
        if self.LA(1) == self.input.STAR:
            self.match('*')
        elif self.LA(1) == self.input.PLUS:
            self.match('+')
        elif self.LA(1) == self.input.QMARK:
            self.match('?')
    
    def atom(self):
        if self.LA(1) == self.input.LPAREN:
            self.sub_rule()
        elif self.LA(1) == self.input.QUOTE:
            self.STRING()
        elif self.LA(1) == self.input.NAME:
            self.rule_invoke()
        else: raise Exception(f"Expecting something; found {self.LT(1)} on Line # {self.LT(1)._line_number}.")
    
    def sub_rule(self):
        self.match('(')
        self.or_tokens()
        self.match(')')
    
    def STRING(self):
        self.match(self.input.STRING)
    
    def rule_invoke(self):
        self.NAME()
    
    def NAME(self):
        self.match(self.input.NAME)

if __name__ == "__main__":
    import sys
    input = \
"""
grammar             : rule *                                    ;
rule                : NAME ':' or_tokens * ';'                  ;

or_tokens           : and_tokens ( '|' and_tokens ) *           ; 
and_tokens          : cmpd_token ( '&' cmpd_token ) *           ;
cmpd_token          : atom ( '*' | '+' | '?' ) ?                ;
atom                : sub_rule | STRING | rule_invoke         ;

sub_rule            : '(' or_tokens ')'                         ; 
STRING              : "'" ~ "'" + "'"                           ;
rule_invoke         : NAME                                      ; 

NAME                : ( a..z ) +                                ;
"""
    drewparser = Parser(input, 2)
    drewparser.grammar()
