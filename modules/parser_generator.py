""" 
    This module contains code for generating a parser from a grammar, 
    (aka a parser generator).


"""

import os

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

    When creating an instance of this class, you must pass in the file path of your grammar file.

    self.__init__() will call self._read_rules_predicates() to load in the rules as lists of rule_tokens
    and predicates as a dict.

    Then, self.__init_() calls self._build_rules() which will fill self.rules (a list) with Nodes.

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

    def __init__(self, grammar_file_path):
        self.rules = []    
        
        self.rule_tokens, self.predicates = self._read_rules_predicates(grammar_file_path)
        
        self._build_rules()

    def dump(self, dump_rules=False, dump_rule_tokens=False, dump_predicates=False):

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
        
        if dump_rule_tokens: 
            print('-'*40)
            print("Rule Tokens:")
            for token_list in self.rule_tokens:
                for token in token_list: 
                    print(token, ' ', end='')
                print()

        if dump_predicates: 
            print('-'*40)
            print("Predicates:")
            for k,v in self.predicates.items(): print(k,'->',v)

        if dump_rules:
            print('-'*40)
            print("Rules:")
            for rule in self.rules:
                n = 2 if len(rule.name) < 7 else 1
                print(f"{rule.name}:"+'\t'*n+'[',end=' ')
                for item in rule.nodes:
                    dive(item)
                print(' ]')

    def _build_rules(self):        
        for rule_list in self.rule_tokens:
        
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

    def _process_rule(self, tokens):
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
        return rule_tokens

    def _read_rules_predicates(self, grammar_file_path):
        """ This function opens the grammar file located at 'grammar_file_path' and reads
            in the rules and predicates.
            
            @ Return:
            rule_tokens - A list of rule_token lists, one per rule
            predicates  - A dict of rule_name to it's predictor (lexical token)
        """
        tokens = []
        rule_tokens = []
        predicates = {}
        with open(grammar_file_path) as f:
            
            # Read in main portion of grammar:
            line = f.readline().rstrip()
            while "PREDICATES" not in line:     
                # Ignore comments:
                if line[0] == '#': line = f.readline(); continue
                
                tokens+=(line.split())
                if len(tokens) == 0: line = f.readline(); continue
                
                if tokens[-1] == ';': 
                    rule_tokens.append(self._process_rule(tokens))
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

        return rule_tokens, predicates

    def generate_source_text(self): 
        """ Using self.rule_tokens and self.predicates, generates python parser code.
            @Return: A list of strings which make up the python parser code
        """
        predicates = self.predicates
        source_code_lines = []
       
        def gen_func_body_statement(child, tab=1):
            """ Accepts a node, 'child', and generates the appropriate python statement, 
                or suite of statements based on what RuleToken type the node is. 
            """
            if child.type == RT.TERMINAL:           # Terminal
                add_line(f"self.match({child.name})", tab)

            elif child.type == RT.NON_TERMINAL:     # Non-Terminal                                       
                add_line(f"self.{child.name}()", tab)
            
            if child.name in ['*', '+']:            # RT.MODIFIER
                condition   = child.nodes[-1].name[5:] # Extract the loop end condition
                condition   = condition.split(',')

                comp        = child.nodes[-1].name[3:5] # Extract the comparison operator
                suite       = child.nodes[0] 

                if child.name == '+': # 1 or more of the previous token, so force match 1 time:
                    gen_func_body_statement(suite, tab)

                foo = f"while self.LA(1) {comp} self.input.{condition[0]}"
                if len(condition) > 1: 
                    for cond in condition[1:]:
                        foo += f" or self.LA(1) {comp} self.input.{cond}"
                add_line(foo+':', tab)

                gen_func_body_statement(suite, tab+1)

            elif child.name == '|':              # RT.MODIFIER: This OR this OR this

                def build_stat(token, predicates, if_or_elif):
                    """ Soley used for building if-elif suites.
                        Also handles using booleans in building the tests: 
                            
                            >>> if x or y: pass
                            >>> if x and y: pass
                            
                        """
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

                    cur_line = f"{keyword} self.LA(1) == self.input.{predictor[0]}"
                    predictor.pop(0)

                    if op == "or":
                        # If one of the alternates has multiple predictors, handle them:
                        for p in predictor:
                            cur_line += f" {op} self.LA(1) == self.input.{p}"

                    if op == "and":       
                        i = 2             
                        # If one of the alternates requires multiple predictors, handle them:
                        for p in predictor:
                            cur_line += f" {op} self.LA({i}) == self.input.{p}"
                            i += 1
                    
                    cur_line += ':'
                    return cur_line

                # The first test will always be an 'if' statment:
                add_line(build_stat(child.nodes[0], predicates, 'if'), tab)  # Add the test line
                gen_func_body_statement(child.nodes[0], tab+1)                # Generate the body 
                suite = child.nodes[1:]                                      # Remove generated line from list

                # Any subsequent test will be an elif statement: 
                for node in suite:
                    add_line(build_stat(node, predicates, 'elif'), tab)  # Generate test line
                    gen_func_body_statement(node, tab+1)                  # Generate the body 

            elif child.type == RT.SUB_RULE:    
                for sub_child in child.nodes:
                    gen_func_body_statement(sub_child, tab)
        
        # For each rule in self.rules, generate source code for that rule:
        RT = RuleToken
        for rule in self.rules:
            source_code_lines.append('    ') # Insert blank line between func defs
            tab = 1
            def add_line(text, tab=0): 
                source_code_lines.append('    '*tab+text)

            # Generate the function name:
            add_line(f"def {rule.name}(self):", tab); tab += 1

            # Temporary while I better integrate my grammar and token_defs
            if rule.name in ["NAME", "NUMBER"]: 
                add_line(f"self.match(self.input.{rule.name})", tab)  
                continue

            # Generate the function body for a rules function.
            for child in rule.nodes:
                gen_func_body_statement(child, tab)
        
        return source_code_lines

if __name__ == "__main__":
    path = os.getcwd() 
    g = ParserGenerator(path+"\\DrewGrammerLimitedV1.txt")
    g.dump(dump_rules=True)
    code = g.generate_source_text()
    #for line in code: print(line)

    """ 
    TODO: 

    *   rename this module to not be 'grammar_tree' becaues it ain't that anymore

    *   Work on plan to consolidate token_defs and grammar
    *   Work on removing hard coded implemenation details from dlexer.py and lexer.py: 
            > Currently, to add NEW tokens to support new items in the grammar I have to:
                > Add the token def to the token_defs.txt file
                > Add the token name as an int to the dlexer.py file
                > If it's a multichar token, add it to the lexer method in lexer.py

            > I don't like that, it should all be generated from the grammar file.
    
    
    """
