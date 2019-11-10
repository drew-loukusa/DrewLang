""" 
    This module contains code for generating a parser from a grammar, 
    (aka a parser generator).


"""


class RuleToken:
    RULE_NAME = 0
    NON_TERMINAL = 1
    TERMINAL = 2
    MODIFIER = 3
    MODIFIER_INFO = 4
    SUB_RULE = 5

    type_names = ["RULE_NAME","NON_TERMINAL","TERMINAL","MODIFIER","MODIFIER_INFO","SUB_RULE"]

    def __init__(self, name, token):
        self.type = name
        self.text = token 
        self.sub_list = []

    def __str__(self):
        if len(self.sub_list) > 0:
            rep = f"<{self.type_names[self.type]}; ["
            for token in self.sub_list:
                rep+= f"{token}, "
            rep += "]>"
            return rep
        return f'<{self.type_names[self.type]}; "{self.text}">'

class Node:
    def __init__(self, name, ntype):
        self.name = name 
        self.type = ntype
        self.nodes = [] # A list of nodes

    def __str__(self):        
        def_list = ""
        for item in self.nodes:
            if item: def_list += f"{item.name}, "
        return f"{self.name}; [{def_list}]"

class ParserGenerator:
    """
    The purpose of this class is... TODO: Write this <-----
    General Overview: 

    When creating an instance of this class, if you pass in rule_tokens on creation, __init__ will call
    self._build_rules().

    self._build_rules() will fill self.rules (a list) with Nodes.

    Each Node in self.rules has: 'name' (rule name), 'type' (terminal, non-terminal, etc etc), 
    and 'nodes' (a list of nodes which make up the rule definition).

    For each Node in a rules 'definition' list, that Node could be one of several types: 

            NON_TERMINAL    ;       These are nodes containg only 'name' and 'type'. 
            TERMINAL        ;       
             MODIFIER_INFO  ;


            MODIFIER        ;       These nodes have 'name' 'type' AND their own list of nodes           
            SUB_RULE        ;       SUB_RULE contains a list of nodes that define said sub_rule
                                    And modifier ('*' or '|') contain a list of nodes which are being modified. 
    """ 

    def __init__(self, rule_tokens=None):
        self.rules = []    

        if rule_tokens: self._build_rules(rule_tokens)

    def dump(self):

        def dive(item):
            if item.name in ['*', '|', '+', "SUB_RULE"]:                 
                print(f"'{item.name}' -> [ ", end='')
                rep = ""
                for node in item.nodes:
                    if node.name in ['*', '|', '+', "SUB_RULE"]: dive(node)
                    else: rep += f"{node.name}, "
                rep += ' ]'
                print(rep, end=', ')
            else: print(f"{item.name}", end=', ')

        for rule in self.rules:
            n = 2 if len(rule.name) < 7 else 1
            print(f"{rule.name}:"+'\t'*n+'[',end=' ')
            for item in rule.nodes:
                dive(item)
            print(' ]')

    def _build_rules(self, rule_tokens):
        """ rule_tokens is a list of rule_token lists """
        for rule_list in rule_tokens:
        
            rule_name,rule = rule_list[0].text, None  
            rule = Node(rule_name, rule_list[0].type)    
            self.rules.append(rule)

            definition_list = rule_list[1:] # Remove rule_name token from list
            #print(f"sub-root: {rule}")
            self._build_definition(rule, definition_list)

    def _build_definition(self, rule, rule_list):
        #print(".........................")
        #print("Top of build_def():")
        #print(f"Current rule: {rule}")
        last = None
        last_was_or_node = False
        for rule_token in rule_list:
            child = None

            if rule_token.type == RuleToken.NON_TERMINAL:                 
                child = Node(rule_token.text, rule_token.type)
                
            elif rule_token.type == RuleToken.TERMINAL: 
                child = Node(rule_token.text, rule_token.type)

            elif rule_token.type == RuleToken.MODIFIER: 
                #We need to grab the last node since it is being modified
                if rule_token.text in ['*', '+']:
                    last = rule.nodes.pop()
                    child = Node(rule_token.text, rule_token.type)
                    child.nodes.append(last)

                if rule_token.text == '|': 
                    last_was_or_node = True
                    
                    if rule.nodes[-1].name == '|': continue
                    
                    last = rule.nodes.pop()
                    child = Node(rule_token.text, rule_token.type)
                    child.nodes.append(last)

                # if rule_token.text == '+': 
                #     continue # Will implement later

            elif rule_token.type == RuleToken.MODIFIER_INFO: 
                # The last node should be a '*' or a '+' node. So put this info in the def for it
                child = rule.nodes.pop()
                node = Node(rule_token.text, rule_token.type)
                child.nodes.append(node)

            elif rule_token.type == RuleToken.SUB_RULE:
                child = Node("SUB_RULE", rule_token.type)                
                self._build_definition(child, rule_token.sub_list)
                #child = child.nodes[0] # Make child the 'or' node instead of SUB_RULE

            # If the last node was an 'or node', then we need 
            # to put the current node as the 'or' node's right child:
            if last_was_or_node and len(rule.nodes) > 0:                 
                last = rule.nodes.pop()
                last.nodes.append(child)
                last_was_or_node = False
                child = last

            # Add child to the rules nodes (list):
            #print(f"Adding {child} to rule def...")
            rule.nodes.append(child)            

    def generate_source_text(self, predicates): 
        # Recursively iterate through all nodes in tree, generating source code 
        # Put rule names into self.generated (dict) as they are generated.
        RT = RuleToken
        for rule in self.rules:
            print()
            tab = 1
            def tab_print(text, tab=0): print('    '*tab+text)

            # Yeet out the rule name:
            tab_print(f"def {rule.name}(self):", tab); tab += 1

            if rule.name in ["NAME", "NUMBER"]: # Temporary while I better integrate my grammar and token_defs
                tab_print(f"self.match(self.input.{rule.name})", tab)  
                continue

            # NOTE: Also try to figure out how to generate recognizers 
            # for NUMBER, NAME and maybe 'string' from the grammar.

            # And give more thought to how to integrate the token_defs
            # and the grammar together.
            def generate_rule(child, tab=1):
                if child.type == RT.TERMINAL: # Terminal
                    tab_print(f"self.match({child.name})", tab)

                elif child.type == RT.NON_TERMINAL: # Non-Terminal                                       
                    tab_print(f"self.{child.name}()", tab)
                
                if child.name in ['*', '+']: # RT.MODIFIER
                    condition   = child.nodes[-1].name[5:] # Extract the loop end condition
                    condition   = condition.split(',')

                    comp        = child.nodes[-1].name[3:5] # Extract the comparison operator
                    suite       = child.nodes[0] 

                    if child.name == '+': # 1 or more of the previous token, so force match 1 time
                        generate_rule(suite, tab)

                    foo = f"while self.LA(1) {comp} self.input.{condition[0]}"
                    if len(condition) > 1: 
                        for cond in condition[1:]:
                            foo += f" or self.LA(1) {comp} self.input.{cond}"
                    tab_print(foo+':', tab)

                    generate_rule(suite, tab+1)

                elif child.name == '|': # RT.MODIFIER

                    def build_stat(token, predicates, if_or_elif):
                        predictor,keyword, op = [], None, None
                        if if_or_elif == 'if':
                            keyword = 'if'
                            predictor = predicates[token.name]
                        if if_or_elif == 'elif':
                            keyword = 'elif'
                            predictor = predicates[token.name]
                        if '&' in predictor: 
                            predictor = predictor.split('&')
                            op = "and"
                        elif '|' in predictor: 
                            predictor = predictor.split('|')
                            op = 'or'
                        else: predictor = [predictor]

                        #print(f"predictor: {predictor}")

                        cur_line = f"{keyword} self.LA(1) == self.input.{predictor[0]}"
                        predictor.pop(0)

                        #print(f"predictor: {predictor}")

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

                    tab_print(build_stat(child.nodes[0], predicates, 'if'), tab)
                    generate_rule(child.nodes[0], tab+1)
                    suite = child.nodes[1:]
                    for node in suite:
                        tab_print(build_stat(node, predicates, 'elif'), tab)
                        generate_rule(node, tab+1)
                
                elif child.type == RT.SUB_RULE: 
                    for sub_child in child.nodes:
                        generate_rule(sub_child, tab)

            for child in rule.nodes:
                generate_rule(child, tab)

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
    
    #NOTE: RULE_TOKEN DUMP: 
    # for token in rule_tokens: 
    #     print(token, ' ', end='')
    # print()
    
    return rule_tokens

if __name__ == "__main__":
    import os
    path = os.getcwd() 

    tokens = []
    rule_tokens = []
    predicates = {}
    print("cwd:",os.getcwd())
    with open(path+"\\DrewGrammerLimitedV1.txt") as f:
        
        # Read in main portion of grammar:
        line = f.readline().rstrip()
        while "PREDICATES" not in line:     
            # Ignore comments:
            if line[0] == '#': line = f.readline(); continue
            
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
            # Ignore comments: 
            if line[0] == '#': line = f.readline(); continue

            tokens = line.split()
            
            if len(tokens) == 0: line = f.readline() ; continue
            if tokens[0] == "END": break

            rule_name, predictor = tokens[0], tokens[2]
            predicates[rule_name] = predictor
            line = f.readline() 
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    #for k,v in predicates.items(): print(k,'->',v)
    g = ParserGenerator(rule_tokens)    
    #g.dump()
    g.generate_source_text(predicates)
