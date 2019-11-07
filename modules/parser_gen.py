import os

class RuleToken:
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
    rule_tokens.append(RuleToken("rule_name", tokens[0])) ; tokens.pop(0); tokens.pop(0)

    def rules(token):
        # Process terminal token:
        if token[0] == "'":    return RuleToken("terminal",token)
        
        # Process modifier token:
        elif token in '*+?|':  return RuleToken("modifier",token)

        # Process modifer info token;
        elif len(token) >= 3 and token[0:3] == 'end':
                                return RuleToken("modifier_info", token)
        else:                   return RuleToken("non_terminal", token)
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == ';': break
       
        # Process sub_rules:
        if token == '(': 
            i += 1; token = tokens[i]

            sub_rule = RuleToken("sub_rule", None)
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

def gen_code(rule_tokens, predicates):
    code_lines = []
    rule_def_str = "def {}(self):"
    #while_str    = "\t\twhile self.LA(1) {comp} self.input.{loop_condition}:"
    def print_code(token, peek1, peek2):
        if token.type == "rule_name":
            code_lines.append(rule_def_str.format(token.text))

        if peek1 and peek1.type == "modifier" and peek1.text == "*":
            loop_condition,comp = peek2.text[5:].split(','), peek2.text[3:5]
            foo = f"while self.LA(1) {comp} self.input.{loop_condition[0]}:"

            if len(loop_condition) > 1: 
                foo = f"while self.LA(1) {comp} self.input.{loop_condition[0]}"
                for cond in loop_condition[1:]:
                    foo += f" or self.LA(1) {comp} self.input.{cond}:"
            code_lines.append(foo)

        if token.type == "non_terminal": 
           code_lines.append(f"self.{token.text}()")

        if token.type == "terminal": 
            code_lines.append(f"self.match(self.getTokenType({token.text}))")

    k = len(rule_tokens)
    for i in range(k):
        token = rule_tokens[i]
        peek1 = None if i+2>=k else rule_tokens[i+1] 
        peek2 = None if i+2>=k else rule_tokens[i+2] 

        print_code(token, peek1, peek2)

        if token.type == "sub_rule": 
            
            predictor = predicates[token.sub_list[0].text]
            code_lines.append(f"if self.LA(1) == self.input.{predictor[0]}:")
            print_code(token.sub_list[0], token.sub_list[1], token.sub_list[2])
            token.sub_list.pop(0)

            for sub_token in token.sub_list:
                if sub_token.text == '|': continue
                predictor = predicates[sub_token.text]
                code_lines.append(f"elif self.LA(1) == self.input.{predictor[0]}:")
                print_code(sub_token, None, None)
                print_code(token, peek1, peek2)
            
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
    line = f.readline().rstrip()
    while "PREDICATES" not in line:     
        tokens+=(line.split())
        if len(tokens) == 0: line = f.readline(); continue
        if tokens[-1] == ';': 
            rule_tokens.append(process_rule(tokens))
            tokens = []
        line = f.readline()

    line = f.readline()
    while "END" != line:
        tokens = line.split()
        
        if len(tokens) == 0: line = f.readline() ; continue
        if tokens[0] == "END": break

        rule_name, predictor = tokens[0], list(tokens[2].split('|'))
        predicates[rule_name] = predictor
        line = f.readline() 

for k,v in predicates.items(): print(f"{k}: {v}")
source_code_lines = []
for sub_list in rule_tokens: 
    source_code_lines += gen_code(sub_list,predicates)

tabs = 1
last_line = source_code_lines[0]
for line in source_code_lines[1:]: 
    if 'def' == line.split()[0]: 
        tab = 1
        print("\t"*tab+line)
    if last_line.split()[0] in ['def','if', 'elif', 'while','else']:
        tab += 1
        print("\t"*tab+line)
    


   


