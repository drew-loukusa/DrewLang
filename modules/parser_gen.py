import os
path = os.getcwd()
path = path[:len(path)-7]
f =  open(path+"DrewGrammerLimitedV1.txt")

class RuleToken:
    def __init__(self, name, token):
        self.name = name
        self.token = token 
    def __str__(self):
        if type(self.token) is list: 
            rep = f"<{self.name}; ["
            for sub_token in self.token:
                rep+= f"{sub_token}, "
            rep += "]>"
            return rep
        return f'<{self.name}; "{self.token}">'

def process_rule(tokens):
    # From line tokens, make a list of rule-tokens
    # Rule token types: rule_name, non_terminal, terminal, modifier, sub_rule

    rule_tokens = []

    # Process rule name and ':':
    rule_tokens.append(RuleToken("rule_name", tokens[0])) ; tokens.pop(0); tokens.pop(0)

    def rules(token):
        if token[0] == "'" or token.isupper():    
                                return RuleToken("terminal",token)

        elif token in '*+?|':  return RuleToken("modifier",token)

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

            sub_rule = RuleToken("sub_rule", [])
            while token != ')':
                sub_rule.token.append(rules(token))
                i += 1; token = tokens[i]
            rule_tokens.append(sub_rule)

        else: 
            rule_tokens.append(rules(token))
        i += 1
    
    for token in rule_tokens: 
        print(token, ' ', end='')
    print()
    return rule_tokens
def gen_code(rule_tokens):
    for token in rule_tokens:
        if token.name == "rule_name":

            pass

print("~~~~~~~~~~~~~~~~~~~~~~~")
print("~~~~~~~~~~~~~~~~~~~~~~~")
print("~~~~~~~~~~~~~~~~~~~~~~~")

tokens = []
reading = False
for line in f.readlines():
    reading = True
    tokens+=(line.split())
    if len(tokens) == 0: continue
    if tokens[-1] == ';': 
        rule_tokens = process_rule(tokens)
        gen_code(rule_tokens)
        tokens = []
        
   


