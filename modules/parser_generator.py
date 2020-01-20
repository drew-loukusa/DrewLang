""" 
    This module contains code for generating a parser from a grammar, 
    (aka a parser generator)
"""

import os
try:
    from lexer import Lexer
except ImportError:
    pass

class RuleToken:
    RULE_NAME = 0
    NON_TERMINAL = 1
    TERMINAL = 2
    MODIFIER = 3
    MODIFIER_INFO = 4
    SUB_RULE = 5

    type_names = ["RULE_NAME","NON_TERMINAL","TERMINAL","MODIFIER","MODIFIER_INFO","SUB_RULE"]

    def __init__(self, rule_token_type, text):
        self.type = rule_token_type
        self.text = text 
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
        self.name = name    # Literal text of rule
        self.type = ntype   # RuleToken type as a string
        self.nodes = []     # A list of nodes

    def __str__(self):        
        def_list = ""
        for item in self.nodes[:-1]:
            if item: def_list += f"{item.name}, "
        if self.nodes[-1]: def_list += f"{item.name}"

        return f"{self.name}; [{def_list}]"

class GrammarReader:
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
            MODIFIER_INFO   ;


            MODIFIER        ;       These nodes have 'name' 'type' AND their own list of nodes           
            SUB_RULE        ;       SUB_RULE contains a list of nodes that define said sub_rule
                                    And modifier ('*' or '|') contain a list of nodes which are being modified. 
    """ 

    def __init__(self, grammar_file_path="", mode=''):
        self.grammar_file_path = grammar_file_path
        self.rules = []         # List of rules (nodes) 
        self.rules_dict = {}    # The same rules, but stored as a dict:  { rule_name -> rule (Node) }
        self.rule_tokens = []   # List of RuleToken lists
        self.predicates = {}    # Dict of rule_name -> what token predicts said rule

        if mode == 'rule':
            self._read_rules_and_predicates(grammar_file_path) # Fills self.rule_tokens and self.predicates            
            self._build_rules() # Fills self.rules        
            self._generate_predicates()

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
            l_tkns = line.split()
            k,v = l_tkns[0],l_tkns[1]
            if len(l_tkns) >= 3 and l_tkns[1] == "NON_PRE_DEF":  # Generate lexer funcs
                v = l_tkns[2:]
                rule_tokens = self._process_rule(v, mode='token')
                rule_AST = self._build_rule(rule_tokens, mode='token')

                v = rule_AST

            token_defs[k] = v
       
        return token_defs

    def dump(self, dump_rules=False, dump_rule_tokens=False, dump_predicates=False):
        """ 
            Dumps the contents of ParserGenerators data stores.
            Enable the ones you want to dump by setting their named parameters to true.
        """
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
            for k,v in self.predicates.items(): print(k,v)

        if dump_rules:
            print('-'*40)
            print("Rules:")
            for rule in self.rules:
                n = 2 if len(rule.name) < 7 else 1
                print(f"{rule.name}:"+'\t'*n+'[',end=' ')
                for item in rule.nodes:
                    self.print_rule(item)
                print(' ]')

    def print_rule(self, item):
        decend_set = ['*', '|', '+', '~', '?', "SUB_RULE"]
        if item.name in decend_set:                 
            print(f"'{item.name}' -> [ ", end='')
            rep = ""
            for node in item.nodes:
                if node.name in decend_set: self.print_rule(node)
                else: rep += f"{node.name}, "
            rep += ' ]'
            print(rep, end=', ')
        else: print(f"{item.name}", end=', ')
    
    def _build_rules(self):        
        for rule_list in self.rule_tokens:
            self._build_rule(rule_list, mode='rule')
        
    def _build_rule(self, rule_list, mode):
        rule_name,rule = rule_list[0].text, None  

        rule = Node(name="BLANK", ntype=0)
        definition_list = rule_list
        if  mode == 'rule': 
            rule = Node(rule_name, rule_list[0].type)    
            self.rules.append(rule)
            self.rules_dict[rule_name] = rule
            definition_list = rule_list[1:] # Remove rule_name token from list
        
        self._build_definition(rule, definition_list)
        return rule 

    def _build_definition(self, rule, rule_list):
        #print(".........................")
        #print("Top of build_def():")
        #print(f"Current rule: {rule}")

        def get_last_node():
            last = rule.nodes.pop()
            if last.name == "SUB_RULE" and last.nodes[0].type == RuleToken.MODIFIER:
                last = last.nodes[0]
            return last

        def find_next_valid_token(node):
            if node.name in ['|','*','+','~', '?',"SUB_RULE"]:
                node = find_next_valid_token(node.nodes[0])    
            return node 

        last = None
        last_was_or_node = False
        last_was_not = False
        last_was_star = False
        last_was_range = False
        for rule_token in rule_list:
            child = None

            if rule_token.type == RuleToken.NON_TERMINAL:                 
                child = Node(name=rule_token.text, ntype=rule_token.type)
                
            elif rule_token.type == RuleToken.TERMINAL: 
                child = Node(name=rule_token.text, ntype=rule_token.type)

            elif rule_token.type == RuleToken.MODIFIER: 
                #We need to grab the last node since it is being modified
                if rule_token.text in ['*', '+', '?']:
                    if rule_token.text == '*': last_was_star = True
                    last = get_last_node()
                    child = Node(name=rule_token.text, ntype=rule_token.type)
                    child.nodes.append(last)

                if rule_token.text == '|': 
                    last_was_or_node = True
                    
                    if rule.nodes[-1].name == '|': continue
                    
                    last = get_last_node()
                    child = Node(name=rule_token.text, ntype=rule_token.type)
                    child.nodes.append(last)

                if rule_token.text == '..':
                    last_was_range = True 
                    last = get_last_node()
                    child = Node(name=rule_token.text, ntype=rule_token.type)
                    child.nodes.append(last)

                if rule_token.text == '~':
                    last_was_not = True
                    child = Node(name=rule_token.text, ntype=rule_token.type)              

            elif rule_token.type == RuleToken.SUB_RULE:
                child = Node(name="SUB_RULE", ntype=rule_token.type)       
                self._build_definition(child, rule_token.sub_list)
                
                # Make the modifier node the child instead of SUB_RULE, since 
                # modifiers only ever serve as root nodes for a tree:
                if child.nodes[0].type == RuleToken.MODIFIER:
                    child = child.nodes[0] 

            # If the last node was an 'or node', then we need 
            # to put the current node as the 'or' node's right child:
            if (last_was_or_node or last_was_not or last_was_range) and rule_token.type != RuleToken.MODIFIER:                 
                last = get_last_node()
                last.nodes.append(child)

                last_was_or_node = False
                last_was_not = False
                last_was_range = False

                child = last

            # IF a token follows after a '*' operator, that token can be used
            # as the end condition for the while loop of the token preceding the '*'.
            # Example: . * 'b' -> means match any char as long it's not 'b'.        
            if last_was_star and rule_token.type != RuleToken.MODIFIER:
                last = get_last_node()
                last.nodes.append(find_next_valid_token(child))
                last_was_star = False
                rule.nodes.append(last)

            # Add child to the rules nodes (list):
            #print(f"Adding {child} to rule def...")
            rule.nodes.append(child)            

    def _process_rule(self, tokens, mode='rule'):
        """ From a list of text-tokens, make and return a list of rule-tokens.
            Rule token types: rule_name, non_terminal, terminal, modifier, sub_rule
        """

        rule_tokens = []

        # Process rule name and ':':
        if mode == 'rule':
            rule_tokens.append(RuleToken(RuleToken.RULE_NAME, tokens[0]))
            tokens.pop(0)
            tokens.pop(0)

        def rules(lexical_token):
            # Process terminal symbols: Predefined and Non-pre-defined            
            if lexical_token[0] == "'" or lexical_token.isupper():  
                return RuleToken(RuleToken.TERMINAL,lexical_token)
            
            # Process modifier lexical_token:
            elif lexical_token in list('*+?|~')+['..']: return RuleToken(RuleToken.MODIFIER,lexical_token)

            # Process modifer info lexical_token;
            elif len(lexical_token) >= 3 and lexical_token[0:3] == 'end':
                                    return RuleToken(RuleToken.MODIFIER_INFO, lexical_token)
            else:                   return RuleToken(RuleToken.NON_TERMINAL, lexical_token)
        i = 0
        while i < len(tokens):
            lexical_token = tokens[i]
            if lexical_token == ';': break
        
            # Process sub_rules:
            def process_sub_rule(lexical_token, i):
                k = i; i += 1; lexical_token = tokens[i]

                rule = RuleToken(RuleToken.SUB_RULE,'SUB_RULE')                
                while lexical_token != ')':
                    if lexical_token == '(': 
                        n, sub_rule = process_sub_rule(lexical_token, i)
                        rule.sub_list.append(sub_rule)
                        i += n
                    else:
                        rule.sub_list.append(rules(lexical_token))
                        i += 1
                    lexical_token = tokens[i]
                i += 1               
                return (i - k), rule

            if lexical_token == '(': 
                n, sub_rule = process_sub_rule(lexical_token, i)
                rule_tokens.append(sub_rule)
                i += n
            else: 
                rule_tokens.append(rules(lexical_token))
                i += 1
        return rule_tokens

    def _read_rules_and_predicates(self, grammar_file_path):

        # TODO: Seperate reading in rules and predicates, then bust any rule reading out into a module and import that stuff

        """ This function opens the grammar file located at 'grammar_file_path' and reads
            in the rules and predicates.
            
            @ Return:
            rule_tokens - A list of rule_token lists, one per rule
            predicates  - A dict of rule_name to it's predictor (lexical token)
        """
        with open(grammar_file_path) as f:
            
            # ------------------------------------------------------------------
            # Read in the rules:
            tokens = []
            while "PREDICATES" not in (line := f.readline()):     
                # Ignore comments and blank lines:
                if line[0] == '#' or len(line.rstrip('\n')) == 0: continue
                
                # Probably should not lex the line using str.split(), 
                # but it WORKS FOR NOW:
                tokens += (line.split())
                
                # Once we've collected a rules worth of tokens, process the rule:
                if tokens[-1] == ';': 
                    self.rule_tokens.append(self._process_rule(tokens))
                    tokens = []

            # ------------------------------------------------------------------
            # Read in predicates: (Pre-written predicates are for rules which require
            # 2 tokens of look ahead)
            """ I use what I'm terming 'predicates' to help generate source code. 
                They're not strictly necessary, and I will probably revise
                my generator so that it can extract that info from the grammar itself,
                but for now I have them as their own section in the grammar file.       
            """
            while "END" not in (line := f.readline()):
                # Ignore comments and blank lines:
                if line[0] == '#' or len(line.rstrip('\n')) == 0: continue

                tokens = line.split()

                rule_name, predictor = tokens[0], tokens[2]
                self.predicates[rule_name] = predictor

    def _generate_predicates(self):
        # ------------------------------------------------------------------
        # Generate predicates from rules:
        lex = Lexer("test", self.grammar_file_path) # Create lexer so we can use DLexer.getTokenNameFromText
      
        self.rules.reverse()         # Build predicates bottom up 

        def build_predicate_text(node):             
            #print('(', node.name, ',', end='')
            #print("trying to get predictor for:", node.name)   
            name = node.name
            
            # If name is double quoted, make it single quoted:
            if len(name) >= 3:
                if  name[0] == r"'" and name[-1] == r"'":
                    name = name[1:-1]
                     
            result = lex.getTokenNameFromText( name ) 
            if result == "NOT_A_TOKEN": 
                if result not in self.predicates: 
                    build_predicate(self.rules_dict[name])
                return self.predicates[name]
            else: return result

        def build_predicate(rule):
            #print("Building predicate for:", rule.name)
            if rule.name in ("program","NAME", "NUMBER"): return  

            if rule.name in self.predicates: return         
            
            name = rule.name 
            fnode = rule.nodes[0]
            
            predictor = ""

            if fnode.name == "SUB_RULE": # Reach in, get the actual first node
                fnode = fnode.nodes[0]

            if fnode.name == "|": 
                token_names = [ build_predicate_text( node ) for node in fnode.nodes ]                        
                predictor = '|'.join(token_names)
            
            elif fnode.name in '*+':
                predictor = build_predicate_text( fnode.nodes[0] )
            
            else: 
                predictor = build_predicate_text( fnode )
            
            # Temporary........................................... see init in lexer? for info
            if name == "STRING": predictor = 'STRING'
            self.predicates[name] = predictor
            #print("Preds:", self.predicates)

        for rule in self.rules: 
            build_predicate(rule)
        
        for token_text in lex.char_to_ttype:
            key = token_text
            #if token_text not in ["NAME", "NUMBER", "STRING"]: # Give quotes to terminals
                #key = "'" + token_text + "'"
            self.predicates[key] = lex.getTokenNameFromText(token_text)

        self.rules.reverse()

class ParserGenerator( GrammarReader ):

    def __init__(self, grammar_file_path):
        super().__init__(grammar_file_path, mode='rule')
        self.source_code = []   # A list containing each line of generated source code 

    def _strip_quotes(self, name):
        """ Strips single quotes on both sides of a string if present"""
        if len(name) >= 3 and name[0] == r"'" and name[-1] == r"'":
            return name[1:-1]
        return name 

    def build_cmpd_stat(self, token, keyword, end_conditon=None):
        """ Returns a complete if/elif/while statement """
        predictor = []
        name = self._strip_quotes(token.name)                
        predictor = self.predicates[name]         

        preds = []
        for p in predictor.split('|'):                            
            if '&' in p:                        
                p = p.split('&')                                
            preds.append(p)
        
        cur_line = f"{keyword} "
        comp_op = '=='
        
        if keyword == 'while' and end_conditon:
            name = self._strip_quotes(end_conditon.name)
            preds = [self.predicates[name]]    
            comp_op = '!='    

        # Construct a test statement using the look ahead set for the given rule we might want to parse:
        for k,p in enumerate(preds, start=1):
            if type(p) is list:   # List means x AND y AND z etc etc
                if k > 1: cur_line += ' or '
                cur_line += " ("
                for i,sub_p in enumerate(p, start=1):
                    if i > 1: cur_line += " and "
                    cur_line += f"self.LA({i}) {comp_op} self.input.{sub_p}"
                cur_line += ") "
            else:
                if k > 1: cur_line += " or "
                cur_line += f"self.LA(1) {comp_op} self.input.{p}"
        cur_line += ':'
        
        return cur_line

    def add_line(self, text, tab=0): 
        self.source_code.append('    '*tab+text)

    def generate_source_text(self, header, footer): 
        """ Using self.rule_tokens and self.predicates, generates python parser code.
            @Return: A list of strings which make up the python parser code
        """        
        self.source_code += header
       
        def gen_func_body_statement(child, tab=1, optional=False):
            """ Accepts a node, 'child', and generates the appropriate python statement, 
                or suite of statements based on what RuleToken type the node is. 
            """
            if child.type in [RT.TERMINAL, RT.NON_TERMINAL]:           
                ltab = tab 
                if optional:                     
                    self.add_line(
                        self.build_cmpd_stat(token=child, keyword='if'),
                        ltab
                    )
                    ltab += 1

                if child.type == RT.TERMINAL:
                    match_text = child.name
                    if match_text.isupper(): 
                        match_text = f"self.input.{match_text}"
                    self.add_line(f"self.match({match_text})", ltab)
                else:
                    self.add_line(f"self.{child.name}()", ltab)
            
            if child.name in ['*', '+'] and len(child.nodes) > 0:            # RT.MODIFIER             

                # These modifiers ONLY ever operate on a single rule (node) 
                # at at time, and the operand is stored in child.nodes[0]: 
                sub_child  = child.nodes[0]    

                # Set loop end condition, if one exists: 
                end_conditon = None if len(child.nodes) < 2 else child.nodes[1]

                # If the operand is a sub_rule...
                if sub_child.name == "SUB_RULE": sub_child = sub_child.nodes[0] # This is problematic if sub_child contains multiple rules in a list like ( ',' NAME )
                
                suite       = child.nodes[0]    # Maybe make function for parsing predicates, maybe stick those in a data structure instead of string...

                if child.name == '+': # 1 or more of the previous token, so force match 1 time:
                    gen_func_body_statement(suite, tab)

                self.add_line(
                    text=self.build_cmpd_stat(sub_child, 'while', end_conditon=end_conditon),
                    tab=tab
                )

                gen_func_body_statement(suite, tab+1)
            
            elif child.name in '|':              # RT.MODIFIER: This OR this OR this

                # The first test will always be an 'if' statment:
                self.add_line(
                    text=self.build_cmpd_stat(child.nodes[0], keyword='if'), 
                    tab=tab
                )  # Add the test line
                gen_func_body_statement(child.nodes[0], tab+1)                # Generate the body 
                suite = child.nodes[1:]                                      # Remove generated line from list

                # Any subsequent test will be an elif statement: 
                for node in suite:
                    self.add_line(                                       # Generate test line
                        text=self.build_cmpd_stat(node, keyword='elif'), 
                        tab=tab
                    )                                               
                    gen_func_body_statement(node, tab+1)            # Generate the body 
                
                if not optional:
                    else_clause = "else: raise Exception(f\"Expecting something; found {self.LT(1)} on Line {self.LT(1)._line_number}.\")"
                    self.add_line(else_clause, tab)
           
            # Handle optional tokens:
            elif child.name == '?':
                # Any statements generated below will not raise exceptions if they fail to parse ... kinda
                gen_func_body_statement(child.nodes[0], tab, optional=True)

            elif child.type == RT.SUB_RULE:    
                for sub_child in child.nodes:
                    gen_func_body_statement(sub_child, tab, optional)
            
        
        # For each rule in self.rules, generate source code for that rule:
        RT = RuleToken
        for rule in self.rules:
            self.source_code.append('    ') # Insert blank line between func defs
            tab = 1

            # Generate the function name:
            self.add_line(f"def {rule.name}(self):", tab); tab += 1

            # Temporary while I better integrate my grammar and token_defs
            if rule.name in ["NAME", "NUMBER", "STRING", "TERMINAL"]: 
                self.add_line(f"self.match(self.input.{rule.name})", tab)  
                continue

            # Generate the function body for a rules function.
            for child in rule.nodes:
                gen_func_body_statement(child, tab)
        
        self.source_code += footer
        return self.source_code

if __name__ == "__main__":
    import sys
    
    path = os.getcwd() 
    
    print("CWD:", path, file=sys.stderr)
    
    grammar_file = "C:\\Users\\Drew\\Desktop\\Code Projects\\DrewLangPlayground\\DrewLang\\DrewGrammar.txt"
    #grammar_file = "C:\\Users\\Drew\\Desktop\\Code Projects\\DrewLangPlayground\\DrewLang\\grammar_grammar.txt"
    g = ParserGenerator(grammar_file)

    g.dump(dump_rules=True, dump_predicates=True)
   
    header = [line.rstrip('\n') for line in open(path+"\\modules\\parser_gen_content\\parser_header.py")]
    footer = [line.rstrip('\n') for line in open(path+"\\modules\\parser_gen_content\\parser_footer.py")]
    
    code = g.generate_source_text(header, footer)

    outpath = path+"\\modules\\gen_parser_test.py"
    #outpath = path + "\\modules\\grammar_parser.py" 

    # Write code to file:
    # --------------------------------------------------
    with open(outpath, mode='w') as f:
        for line in code: f.write(line+'\n')

    #for line in code: print(line)