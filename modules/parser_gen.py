""" 
This module contains a messy parser generator.

It reads in my grammar from DrewGrammarLimitedV1.txt and
creates a parser file which can parse my language. 

Currently my parser is WEAK since it doesn't do anything but parse.

Anyways.

NOTE: I will at somepoint redesign this whole fuckin thing.

I think the grammar of my grammar (wow how meta) could be represented 
in as a tree. I think it would make for a more understandable 
interface if I made something that read in the grammar to a tree data
structure and then we generated source code by walking said tree.

HMMMMMMMMMMMMMM.

"""


import os

header = """
from d_lexer import DLexer
import time

class Parser:
    def __init__(self, input, k):
        self.input = DLexer(input) 
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
        if self.LA(1) == x: # x is token_type 
            self.consume()
        else:
            raise Exception(f"Expecting {self.input.getTokenName(x)}; found {self.LT(1)}.")

"""
class RuleToken:
    RULE_NAME = 0
    NON_TERMINAL = 1
    TERMINAL = 2
    MODIFIER = 3
    MODIFIER_INFO = 4
    SUB_RULE = 5
    def __init__(self, name, token):
        self.type = name
        self.text = token 
        self.sub_list = []

    def __str__(self):
        if len(self.sub_list) > 0:
            rep = f"<{self.type}; ["
            for token in self.sub_list:
                rep+= f"{token}, "
            rep += "]>"
            return rep
        return f'<{self.type}; "{self.text}">'

def process_rule(tokens):
    # From line tokens, make a list of rule-tokens
    # Rule token types: rule_name, non_terminal, terminal, modifier, sub_rule

    rule_tokens = []

    # Process rule name and ':':
    rule_tokens.append(RuleToken(RuleToken.RULE_NAME, tokens[0])) ; tokens.pop(0); tokens.pop(0)

    def rules(token):
        # Process terminal token:
        if token[0] == "'":    return RuleToken(RuleToken.TERMINAL,token)
        
        # Process modifier token:
        elif token in '*+?|':  return RuleToken(RuleToken.MODIFIER,token)

        # Process modifer info token;
        elif len(token) >= 3 and token[0:3] == 'end':
                                return RuleToken(RuleToken.MODIFIER_INFO, token)
        else:                   return RuleToken(RuleToken.NON_TERMINAL, token)
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == ';': break
       
        # Process sub_rules:
        if token == '(': 
            i += 1; token = tokens[i]

            sub_rule = RuleToken(RuleToken.SUB_RULE, None)
            while token != ')':
                sub_rule.sub_list.append(rules(token))
                i += 1; token = tokens[i]
            rule_tokens.append(sub_rule)

        else: 
            rule_tokens.append(rules(token))
        i += 1
    
    for token in rule_tokens: 
        print(token, ' ', end='')
    print()
    return rule_tokens

tab = '    '

def gen_code(rule_tokens, predicates):
    code_lines = []
    rule_def_str = "\n    def {}(self):"
    #while_str    = "\t\twhile self.LA(1) {comp} self.input.{loop_condition}:"
    def gen_line(token, peek1, peek2,n=0):
        
        if peek1 and peek1.type == RuleToken.MODIFIER and peek1.text == "*":
            loop_condition,comp = peek2.text[5:].split(','), peek2.text[3:5]
            foo = f"while self.LA(1) {comp} self.input.{loop_condition[0]}:"

            if len(loop_condition) > 1: 
                foo = f"while self.LA(1) {comp} self.input.{loop_condition[0]}"
                for cond in loop_condition[1:]:
                    foo += f" or self.LA(1) {comp} self.input.{cond}:"
            code_lines.append(tab*n+foo)
            n += 1
            
        if token.type == RuleToken.NON_TERMINAL: 
            if token.text in ["NAME", "NUMBER"]:
                code_lines.append(tab*n+f"self.match(self.input.{token.text})")    
            else:
                code_lines.append(tab*n+f"self.{token.text}()")

        if token.type == RuleToken.TERMINAL: 
            code_lines.append(tab*n+f"self.match(self.input.getTokenType({token.text}))")
        
        if token.type == RuleToken.SUB_RULE: 
            
            def build_stat(token, predicates, if_or_elif):
                predictor,keyword, op = [], None, None
                if if_or_elif == 'if':
                    keyword = 'if'
                    predictor = predicates[token.sub_list[0].text]
                if if_or_elif == 'elif':
                    keyword = 'elif'
                    predictor = predicates[token.text]
                if '&' in predictor: 
                    predictor = predictor.split('&')
                    op = "and"
                elif '|' in predictor: 
                    predictor = predictor.split('|')
                    op = 'or'
                else: predictor = [predictor]

                print(f"predictor: {predictor}")

                cur_line = tab*n+f"{keyword} self.LA(1) == self.input.{predictor[0]}"
                predictor.pop(0)

                print(f"predictor: {predictor}")

                if op == "or":
                    for p in predictor:
                        cur_line += f" {op} self.LA(1) == self.input.{p}"

                if op == "and":       
                    i = 2             
                    for p in predictor:
                        cur_line += f" {op} self.LA({i}) == self.input.{p}"
                        i += 1
                
                cur_line += ':'
                return cur_line
            
            cur_line = build_stat(token, predicates, 'if')

            code_lines.append(cur_line)
            gen_line(token.sub_list[0], token.sub_list[1], token.sub_list[2], n+1)
            token.sub_list.pop(0)

            for sub_token in token.sub_list:
                if sub_token.text == '|': continue
                cur_line = build_stat(sub_token, predicates, 'elif')
                code_lines.append(cur_line)
                gen_line(sub_token, None, None, n+1)
                #print_code(token, peek1, peek2)

    k = len(rule_tokens)
    n = 1
    for i in range(k):
        token = rule_tokens[i]
        peek1 = None if i+2>=k else rule_tokens[i+1] 
        peek2 = None if i+2>=k else rule_tokens[i+2] 

        if token.type == RuleToken.RULE_NAME:
            n = 1
            code_lines.append(tab*n+rule_def_str.format(token.text))
            n = 2
           
        gen_line(token, peek1, peek2, n=n)

    return code_lines

print("~~~~~~~~~~~~~~~~~~~~~~~")
print("~~~~~~~~~~~~~~~~~~~~~~~")
print("~~~~~~~~~~~~~~~~~~~~~~~")

path = os.getcwd()
path = path[:len(path)-7]

tokens = []
rule_tokens = []
predicates = {}
with open(path+"DrewGrammerLimitedV1.txt") as f:
    
    # Read in main portion of grammar:
    line = f.readline().rstrip()
    while "PREDICATES" not in line:     
        tokens+=(line.split())
        if len(tokens) == 0: line = f.readline(); continue
        if tokens[-1] == ';': 
            rule_tokens.append(process_rule(tokens))
            tokens = []
        line = f.readline()

    # Read in predicates: I use what I'm terming 'predicates' to help generate 
    # source code. They're not strictly necessary, and I will probably revise
    # my generator so that it can extract that info from the grammar itself,
    # but for now I have them as their own section in the grammar file.
    line = f.readline()
    while "END" != line:
        tokens = line.split()
        
        if len(tokens) == 0: line = f.readline() ; continue
        if tokens[0] == "END": break

        rule_name, predictor = tokens[0], tokens[2]
        predicates[rule_name] = predictor
        line = f.readline() 

for k,v in predicates.items(): print(f"{k}: {v}")
source_code_lines = []

# NOTE: You can use the rule_tokens generated to build a tree structure 

for sub_list in rule_tokens: 
    source_code_lines += gen_code(sub_list,predicates)
    
with open("gen_parser_test.py", mode='w') as f:
    f.write(header)
    for line in source_code_lines:
        f.write(line+'\n')
    
    footer = """

if __name__ == "__main__":
    import sys
    input = \
\"\"\"x=0;
print("Helloworld");
if(x==0){
    print("xis0");
    print(x);
    x=1;
}
\"\"\"
    drewparser = Parser(input, 2)
    drewparser.program()
    """    
    f.write(footer)

   


