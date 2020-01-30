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
    LPAREN = 5
    RPAREN = 6
    SUB_RULE = 7

    type_names = [  "RULE_NAME","NON_TERMINAL","TERMINAL","MODIFIER",
                    "MODIFIER_INFO", "LPAREN", "RPAREN", "SUB_RULE"]

    def __init__(self, rule_token_type, text):
        self.type = rule_token_type
        self.text = text 

    def __str__(self):
       return f'<{self.type_names[self.type]}; "{self.text}">'

class Node:
    def __init__(self, name, ntype):
        self.name = name    # Literal text of rule
        self.type = ntype   # RuleToken type as a string
        self.nodes = []     # A list of nodes

        # AST Information:
        self.is_root = None
        self.is_child = None 

    def __str__(self):        
        def_list = ""
        for item in self.nodes[:-1]:
            if item: 
                if item.name == '^':
                    def_list += f"{item.name} {item.nodes[0]}"
                else:
                    def_list += f"{item.name}, "
                    
        if self.nodes[-1]: def_list += f"{item.name}"

        return f"{self.name}; [{def_list}]"

class GrammarReader:
    """
    The purpose of this class is... TODO: Write this <-----
    General Overview: 

    When creating an instance of this class, you must pass in the file path of your grammar file.

    self.__init__() will call self._read_rules_predicates() to load in the rules as lists of rule_tokens
    and predicates as a dict.

    Then, self.__init_() calls self._build_rules_from_RuleTokens() which will fill self.rules (a list) with Nodes.

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

        self.prefix_mods   = ['^', '~']
        self.infix_mods    = ['|', '..']
        self.postfix_mods  = ['*', '?', '+']

        self.modifiers = self.prefix_mods + self.infix_mods + self.postfix_mods 

        if mode == 'rule':
            self._read_rules_and_predicates(grammar_file_path) # Fills self.rule_tokens and self.predicates            
            self._build_rules_from_RuleTokens() # Fills self.rules        
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
            
            lexical_tkns = line.split()            
            k,v = lexical_tkns[0:2]

            if len(lexical_tkns) >= 3 and lexical_tkns[1] == "NON_PRE_DEF":  # Generate lexer funcs
                v = lexical_tkns[2:]
                rule_tokens = self._convert_text_to_RuleTokens(v, mode='token')
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

        def name_of_(item):
            if item.is_root:
                return "^"+item.name 
            elif item.is_child:
                return 'c>'+item.name
            return item.name

        decend_set = ['*', '|', '+', '~', '?', "SUB_RULE"]
        if item.name in decend_set:                 
            print(f"'{name_of_(item)}' -> [ ", end='')
            rep = ""
            for node in item.nodes:
                if node.name in decend_set: self.print_rule(node)
                else: rep += f"{name_of_(node)}, "
            rep += ' ]'
            print(rep, end=', ')        
        else: 
            print(f"{name_of_(item)}", end=', ')
    
    def _build_rules_from_RuleTokens(self):        
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

        def get_prev_node():
            return  rule.nodes.pop()            

        def find_next_valid_token(node):
            if node.name in self.modifiers + ["SUB_RULE"]:
                node = find_next_valid_token(node.nodes[0])    
            return node 

        prev_node = None
        last_was_prefix     = False
        last_was_infix      = False       
        last_was_star       = False 

        AST_Rewrite         = False

        # Handle normal rule:
        while len(rule_list) > 0:        
            rule_token = rule_list.pop(0)

            # If an AST rewrite exists, quit this loop, go to AST rewrite loop.
            if rule_token.text == '->': 
                AST_Rewrite = True
                break 

            child = None

            if rule_token.type == RuleToken.NON_TERMINAL:                 
                child = Node(name=rule_token.text, ntype=rule_token.type)
                
            elif rule_token.type == RuleToken.TERMINAL: 
                child = Node(name=rule_token.text, ntype=rule_token.type)

            elif rule_token.type == RuleToken.MODIFIER: 

                # Create infix and postfix modifer nodes, 
                # and then give them their left child node:
                # -------------------------------------------------------------

                """ Take the most recent previous created node since it is being 
                    "modified" by the current modifier node """
                
                # Postfix
                if rule_token.text in self.postfix_mods:
                    
                    # Flag for handling optional end conditions:
                    if rule_token.text == '*': 
                        last_was_star = True

                    prev_node = get_prev_node()
                    child = Node(name=rule_token.text, ntype=rule_token.type)
                    child.nodes.append(prev_node)

                # Infix:
                if rule_token.text in self.infix_mods: 
                    last_was_infix = True
                    
                    # Handle succesive ORs in a row: Skip making a new node, 
                    # And put all or-ed items into a single child list                    
                    if rule_token.text == '|' and rule.nodes[-1].name == '|': continue
                    
                    prev_node = get_prev_node()
                    child = Node(name=rule_token.text, ntype=rule_token.type)
                    child.nodes.append(prev_node)

                # Create prefix operator nodes:               
                # -------------------------------------------------------------
                if rule_token.text in self.prefix_mods:
                    last_was_prefix = True
                    child = Node(name=rule_token.text, ntype=rule_token.type)      

            # Sub rules start with a left paren:
            elif rule_token.type == RuleToken.LPAREN:
                child = Node(name="SUB_RULE", ntype=RuleToken.SUB_RULE)       
                self._build_definition(child, rule_list)
                
                # Make the modifier node the child instead of SUB_RULE, since 
                # modifiers only ever serve as root nodes for a tree:
                if  len(child.nodes) == 1 and \
                    child.nodes[0].type == RuleToken.MODIFIER:
                    child = child.nodes[0] 

            # ... And end with a right paren:
            elif rule_token.type == RuleToken.RPAREN: return

            # Assign infix and prefix modfier nodes their right child node:
            # -----------------------------------------------------------------
            # Add the current node to the previous nodes child list:
            if (last_was_infix or last_was_prefix) and rule_token.type != RuleToken.MODIFIER:                 
                prev_node = get_prev_node()
                prev_node.nodes.append(child)

                last_was_infix = False
                last_was_prefix = False

                child = prev_node

            # Handle optional end conditons for '*' operator:
            # -----------------------------------------------------------------
            # IF a token follows after a '*' operator, that token can be used
            # as the end condition for the while loop of the token preceding the '*'.
            # Example: . * 'b' -> means continue to match any char as long it's not 'b'.        
            if last_was_star and rule_token.type != RuleToken.MODIFIER:
                prev_node = get_prev_node()
                prev_node.nodes.append(find_next_valid_token(child))
                last_was_star = False
                rule.nodes.append(prev_node)

            # Add child to the rules nodes (list):
            rule.nodes.append(child)                        
            #print(f"Adding {child} to rule def...")

        # Do "text" conversions: Change ^ ( a | b | c) to ^ a | ^ b | ^ c
        # My code does not allow chained operators like above, so if you 
        # apply root to a sub-rule with ors inside, it will apply the root 
        # to each node for you.

        # No text conversion is actually happening, but that's the best way to explain it.
        # I read in ^( a | b | c ) into a node data structure and perform the ^ application 
        # on that data structure. 

        # At the same time, I'm also changing the '^' from a node into a node field.
        # ^ NAME would look like: Node( '^', Children: Node( NAME ) )
        # Transform that into:
        # Node( NAME, is_root: True )

        def root_symbol_to_field(rule):
            for i, node in enumerate(rule.nodes):
                
                if node.name in self.modifiers + ["SUB_RULE"] and node.name != '^':
                    root_symbol_to_field(node)

                if node.name == '^' and node.nodes[0].name == '|':
                    or_node = node.nodes[0]
                    for sub_node in or_node.nodes:
                        sub_node.is_root = True 
                    rule.nodes[i] = node.nodes[0]

                elif node.name == '^':
                    node.nodes[0].is_root = True
                    rule.nodes[i] = node.nodes[0]

                # Also set child field if there is no AST-Rewrite:
                elif not AST_Rewrite and node.type in \
                    [RuleToken.TERMINAL, RuleToken.NON_TERMINAL]:
                    if not node.is_root:
                        node.is_child = True
        
        root_symbol_to_field(rule)

        if not AST_Rewrite: return 

        # Handle AST Rewrite:        
        rule_list.pop(0) # Pop '^(' 

        def apply_child_root(rule_token, rule, root_set):
            for node in rule.nodes:                    
                if node.is_root or node.is_child: continue 

                if node.name in self.modifiers + ['SUB_RULE']:
                    apply_child_root(rule_token, node, root_set)
                
                if node.name == rule_token.text: 
                    if not root_set[0]: 
                        node.is_root = True
                        root_set[0] = True
                    else:
                        node.is_child = True
                    break
            else:
                return

        root_set = [False]
        while len(rule_list) > 0: 
            rule_token = rule_list.pop(0)
            if rule_token.text == ')': break
            apply_child_root(rule_token, rule, root_set)

    def _convert_text_to_RuleTokens(self, tokens, mode='rule') -> list: 
        """ From a list of text-tokens, make and return a list of rule-tokens.
            Rule token types: rule_name, non_terminal, terminal, modifier
        """

        rule_tokens = []

        # Process rule name and ':':
        if mode == 'rule':
            rule_tokens.append(RuleToken(RuleToken.RULE_NAME, tokens[0]))
            tokens.pop(0)
            tokens.pop(0)

        for lexical_token in tokens:            
            if lexical_token == ';': 
                break # ';' signifies the end of the rule
            
            token_type = None
            # Process terminal symbols: Predefined and Non-pre-defined            
            if lexical_token[0] == "'" or lexical_token.isupper():  
                token_type = RuleToken.TERMINAL

            # Process Parens:
            elif lexical_token == '(': token_type = RuleToken.LPAREN            
            elif lexical_token == ')': token_type = RuleToken.RPAREN
            
            # Process modifier lexical_token:
            elif lexical_token in self.modifiers: 
                token_type = RuleToken.MODIFIER

            # Process modifer info lexical_token;
            elif len(lexical_token) >= 3 and lexical_token[0:3] == 'end':
                token_type =RuleToken.MODIFIER_INFO
            else:                   
                token_type = RuleToken.NON_TERMINAL

            rule_token = RuleToken(token_type, lexical_token)
            rule_tokens.append(rule_token)

        return rule_tokens

    def _read_rules_and_predicates(self, grammar_file_path):

        """ This function opens the grammar file located at 'grammar_file_path' and reads
            in the rules and predicates.
            
            @ Return:
            rule_tokens - A list of rule_token lists, one per rule
            predicates  - A dict of rule_name to it's predictor (lexical token) - These are auto-generated now?
        """        
        with open(grammar_file_path) as f:
            
            def goto_section(start_string):
                while start_string not in f.readline(): pass                

            # Read in the rules:
            # ------------------------------------------------------------------
            #goto_section("GRAMMAR")
            goto_section("AST")
            tokens = []
            while "END" not in (line := f.readline()):     
                # Ignore comments and blank lines:
                if line[0] == '#' or len(line.rstrip('\n')) == 0: continue
                
                # Probably should not lex the line using str.split(), 
                # but it WORKS FOR NOW:
                tokens += (line.split())
                
                # Once we've collected a rules worth of tokens, process the rule:
                if tokens[-1] == ';': 
                    self.rule_tokens.append(self._convert_text_to_RuleTokens(tokens))
                    tokens = []

           
            # Read in predicates: 
            # ------------------------------------------------------------------
            # (Pre-written predicates are for rules which require 2 tokens of look ahead)
            """ I use what I'm terming 'predicates' to help generate source code. 
                They're not strictly necessary, and I will probably revise
                my generator so that it can extract that info from the grammar itself,
                but for now I have them as their own section in the grammar file.       
            """
            goto_section("PREDICATES")
            tokens = []
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

            if name == '^': name = node.nodes[0]
            
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
                if fnode.name[0] == '$': # Ignore artificial AST nodes:
                    fnode = rule.nodes[1]
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

        """ 
        'predictor' is an auto-generated string which describes the lookahead "set" of given rule.
        'predictor might look like:
               
         NAME|STRING&NUMBER|NUMBER
         So the lookahead set here is NAME or STRING + NUMBER or just NUMBER.
        """

        # Parse the lookahead set-string:
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

                new_text = ""

                # AST Stuff:                
                if child.is_child: 
                    new_text = "lnodes.append( "
                if child.is_root:                      
                    if tab > 2:
                        self.add_line("temp = root", tab)                        
                    new_text = "root = "

                # If child is artifcial AST node:
                if child.name[0] == '$': 
                    new_text += f"AST(name='{child.name[1:]}', artificial=True)"
                
                else:
                    if child.type == RT.TERMINAL:
                        match_text = child.name                    
                        # Match non-pre-defined terminal tokens, which are defined in ALL_CAPS
                        if match_text.isupper():
                            match_text = f"self.input.{match_text}"

                        new_text += f"self.match({match_text})"
                        
                    else:
                        new_text += f"self.{child.name}()"
                    
                    if child.is_child: new_text += " )"

                self.add_line(new_text, ltab)

                if child.is_root and tab > 2:  
                    self.add_line("if temp: root.addChild(temp) ", tab)
            
            if child.name in ['*', '+'] and len(child.nodes) > 0:            # RT.MODIFIER             

                # These modifiers ONLY ever operate on a single rule (node) 
                # at at time, and the operand is stored in child.nodes[0]: 
                sub_child  = child.nodes[0]    

                # Set loop end condition, if one exists: 
                end_conditon = None if len(child.nodes) < 2 else child.nodes[1]

                # If the operand is a sub_rule...
                if sub_child.name == "SUB_RULE": 
                    sub_child = sub_child.nodes[0] # This is problematic if sub_child contains multiple rules in a list like ( ',' NAME )
                
                suite       = child.nodes[0] 

                if child.name == '+': # Match 1 or more of the previous token, so force match 1 time:
                    gen_func_body_statement(suite, tab)

                self.add_line(
                    text=self.build_cmpd_stat(sub_child, 'while', end_conditon=end_conditon),
                    tab=tab
                )

                gen_func_body_statement(suite, tab+1)
            
            elif child.name in '|': # RT.MODIFIER: This OR this OR this

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

            # AST Stuff:
            self.add_line(f"root, lnodes = None, []", tab)             

            # Generate the function body for a rules function.
            for child in rule.nodes:
                gen_func_body_statement(child, tab)

            self.add_line("if root: root.children.extend(lnodes); return root", tab)
            self.add_line("else: return lnodes[0]", tab)
        
        self.source_code += footer
        return self.source_code

if __name__ == "__main__":
    import sys
    cwd = os.getcwd()  
    
    grammar_file =  cwd + "\\DrewGrammar.txt"
    #grammar_file = cwd + "\\grammar_grammar.txt"
    g = ParserGenerator(grammar_file)

    g.dump(dump_rules=True, dump_predicates=True)

    #quit()
   
    header = [line.rstrip('\n') for line in open(cwd+"\\modules\\parser_gen_content\\parser_header.py")]
    footer = [line.rstrip('\n') for line in open(cwd+"\\modules\\parser_gen_content\\parser_footer.py")]
    
    code = g.generate_source_text(header, footer)

    outpath = cwd+"\\modules\\gen_parser_test.py"
    #outpath = cwd + "\\modules\\grammar_parser.py" 

    # Write code to file:
    # --------------------------------------------------
    with open(outpath, mode='w') as f:
        for line in code: f.write(line+'\n')

    #for line in code: print(line)