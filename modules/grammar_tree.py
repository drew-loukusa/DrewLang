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

class RuleNode:
    def __init__(self, rule_name):
        self.rule_name = rule_name 
        self.definition = [] # A list of RuleNodes which makeup this rule

    def __str__(self):        
        def_list = ""
        for item in self.definition:
            if item: def_list += f"{item.rule_name}, "
        return f"{self.rule_name}; [{def_list}]"

class RuleTree:
    # 1. Create the root node:
    #    a. Create blank nodes for it's Non-terminal definition tokens
    #    b. Create leaf nodes for it's terminal definition tokens
    #    c. Put each non-terminal token into a dict with def_token_name as key

    # 2. For each subsequent rule, retreive node from dict using rule_name as key
    #       and repeat step 1 a-b 
    def __init__(self, rule_tokens=None):
        self.root = None
        self.rules_dict = {}
        self.rule_order = {}
        self.rule_order_counter = 0
        self.generated = {}

        if rule_tokens: self.build_tree(rule_tokens)
    
    def _dump(self, node: RuleNode, tab=0, depth=0): 
        #if depth == 10: return
        if node: print("  "*tab,node)
        if not node or len(node.definition) == 0: return
        for child in node.definition:
            self._dump(child, tab+1, depth+1)

    def get_or_create(self, rule_name) -> RuleNode:
        if False and rule_name in self.rules_dict: 
            return self.rules_dict[rule_name]
        else:
            node = RuleNode(rule_name)
            self.rules_dict[rule_name] = node  # Assign rule_name -> rule_node
            self.rule_order[rule_name] = self.rule_order_counter
            self.rule_order_counter += 1
            return node

    def build_tree(self, rule_tokens):
        """ rule_tokens is a list of rule_token lists """
        for rule_list in rule_tokens:
            #print("------------------------------------")
            #print("From build_tree():")
            # Setup or retreive root node for each rule:
            rule_name,rule = rule_list[0].text, None
            #print(f"rule_name: {rule_name}")
            if rule_name in self.rules_dict: 
                rule = self.rules_dict[rule_name]
                #print(f"Retrieved {rule_name} from the dict")
            else:
                rule = RuleNode(rule_name)    
                self.rules_dict[rule_name] = rule
                self.root = rule
                #print(f"Set {rule_name} to tree root.")


            definition_list = rule_list[1:] # Remove rule_name token from list
            #print(f"sub-root: {rule}")
            self.build_definition(rule, definition_list)

    def build_definition(self, rule, rule_list):
        #print(".........................")
        #print("Top of build_def():")
        #print(f"Current rule: {rule}")
        last = None
        last_was_or_node = False
        for rule_token in rule_list:
            child = None

            if rule_token.type == RuleToken.NON_TERMINAL: 
                child = self.get_or_create(rule_token.text)

                # This is to avoid referencing higher order rules which could cause
                # cycles in the "tree" (it's kinda a graph?). 

                # There may be a better solution than this, but this works for now...
                # I hope. 
                if rule.rule_name not in ["program","SUB_RULE"] and \
                    self.rule_order[child.rule_name] < self.rule_order[rule.rule_name]:
                    child = RuleNode(child.rule_name)

            elif rule_token.type == RuleToken.TERMINAL: 
                child = RuleNode(rule_token.text)

            elif rule_token.type == RuleToken.MODIFIER: 
                #We need to grab the last node since it is being modified
                if rule_token.text == "*":
                    last = rule.definition.pop()
                    child = RuleNode(rule_token.text)
                    child.definition.append(last)

                if rule_token.text == '|': 
                    last_was_or_node = True
                    last = rule.definition.pop()
                    child = RuleNode(rule_token.text)
                    child.definition.append(last)

                if rule_token.text == '+': 
                    continue # Will implement later

            elif rule_token.type == RuleToken.MODIFIER_INFO: 
                # The last node should be a '*' node. So put this info in the def for it
                child = rule.definition.pop()
                node = RuleNode(rule_token.text)
                child.definition.append(node)

            elif rule_token.type == RuleToken.SUB_RULE:
                child = RuleNode("SUB_RULE")                
                self.build_definition(child, rule_token.sub_list)

            # If the last node was an 'or node', then we need 
            # to put the current node as the 'or' node's right child:
            if last_was_or_node and len(rule.definition) > 0:                 
                last = rule.definition.pop()
                last.definition.append(child)
                last_was_or_node = False
                child = last

            # Add child to the rules definition (list):
            #print(f"Adding {child} to rule def...")
            rule.definition.append(child)            

    def generate_source_text(self, root): 
        # Recursively iterate through all nodes in tree, generating source code 
        # Put rule names into self.generated (dict) as they are generated.
        print(f"\tdef {root.rule_name}(self):")
        for child in root.definition:

            # For '*', '|' and "SUB_RULE", you'll need to step down
            # to the next node. For '|', more than once most likely.

            # NOTE: Also try to figure out how to generate recognizers 
            # for NUMBER, NAME and maybe 'string' from the grammar.

            # And give more thought to how to integrate the token_defs
            # and the grammar together.

            if child.rule_name == '*': pass       
            elif child.rule_name == '|': pass
            elif child.rule_name == "SUB_RULE": pass
            elif child.rule_name.isupper(): pass # Terminal 
            elif child.rule_name.islower(): pass # Non-Terminal

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
    
    # for token in rule_tokens: 
    #     print(token, ' ', end='')
    # print()
    return rule_tokens

if __name__ == "__main__":
    import os
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
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    tree = RuleTree(rule_tokens)
    tree._dump(tree.root)
    for rule, defn in tree.rules_dict.items():
        print(defn)
