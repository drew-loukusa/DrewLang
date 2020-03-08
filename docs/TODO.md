Current TODO:

*   Working on giving parser_generator.py it's OWN lexer. It was previously 
    using pythons line split method to "parse" the lines of the grammar, but 
    I'd like to switch to an actual lexer that won't screw up lexing if you 
    accidentally forget to insert a space between symbols. 

    3/7/2020: I've decided to go with the SET based regex lexing.
    I'll implement that in lexer.py, and then delete parser_gen_lexer.py
    Then I can just use lexer.py in parser_generator.py to lex the grammar file.

    Then I can move on to scoping.

    3/3/2020: 
    Almost done with using regex for non predefined tokens in parser_gen_lexer.py
    Just need to create Tokens 

    Also: I think I may want to transition my regular lexer away from using the GrammarReader
    to help parse non predefined token defs. I could use a regex impl for that.

    Consider this: Tokens are made up of a combo of character classes: Numbers, symbols, and letters

    You could create simple format for describing a token in terms of a set of regexs:
    For example:

    A number would be: 
        
        re('[0-9]+') 
    
    But something like a hex number would be:

        re('0', 'x','[0-9]+')

    Why do it like this instead writing them as WHOLE regexes? Because it allows us to 
    build the token strings incrementally AND check for malformed tokens.

    If we had '0x', that's not a valid hex number since there are no digits on the right.

    But also, it allows us to distinguish between hex and non-hex. In order to lex hex, 
    it has to have a higher lexical priority than regular numbers, otherwise a hex number like
    "0x545" would get lexed as "0", then as a name "x", then as another number "545".

    So we try to lex hex numbers first. BUT, if we try to lex a regular number thinking it's a hex
    number eg '0', then we'll throw an error. That's bad obviously, and that's why we need to use an
    ordered set of regexs to describe non-pre-defined lexical tokens.

    Using an ordered set of regexes will let us do the following: Say we try to lex the number "0" as a hex
    number. We'll use the first regex '0' to lex the '0' but then we'll move the second one. Which in this
    case is just a 'x'. That regex will fail, and then we'll know we're not lexing a hex number, but a 
    regular number. 

    At this point we can rewind the char stream, and try again.



*   Think about: Currently I'm using these RuleTokens in a weird way. They don't entirely
    define the meta-tokens, as in there is not a RuleToken equivelant for each defined 
    meta-token, but I am using the RuleTokens to build the grammar data structure. 

    NOTE: Consider NOT doing this since you might be able to use this very parser_generator
          to construct a new backend for said parser_generator. Maybe flesh out your meta-grammar,
          then use it to make a meta-grammar-parser which you plug into the parser_generator. 
          We'll see I guess. 

    So, they are serving the purpose of lexical tokens. I need to look at improving 
    RuleTokens to better match the meta-token defs? 

    Biggest thing: Look at how you're using them, come up with possible re-factoring plan.

*   In your lexer you currently iterate through all multi_char_lexers to find the appropriate 
    multi char lexer. This is ineffecient. You should add a class field, a dict of some sort, 
    that maps start_sets -> mult_char_lexer. Tokens that share starting chars would be in the 
    same list. Worst case you have to iterate through several to find the correct one, but 
    that's better than the current solution of iterating through ALL of them everytime. 

AST Todo:

*   Grammar support for embedded ^ and AST rewrites is implemented.
    Probably needs to be refactored at some point, but the basic functionality is there.

MISC TODO: 

*   Write tests for parser: Ensure it correctly parses everything in your grammar
    Consider using pytest? Or some other testing framework.

*   Generate ALL predicates from the grammar.
    Currently we can generate all prediactes except for ones that use '&' 
    I think adding support shouldn't be too hard though; I could, for rules that
    have conflicting start tokens  and which thus require more lookahead to use
    the '&' char. That would make generate predicates very easy for my program.

*   Continue to work on gen_parser_test_AST_CODE_EXAMPLE.py:
    Now that you have added '>=' and others as lexical tokens,
    (plus changed how you lex multi-char tokens to make it easier to 
    add multi-char tokens in the future), 
    your job there should be easier. 

    Write some TEST code as well, a short little \_\_name__ == "\_\_main__" thingy like the other modules.

    Give more thought to implementing the ^ operator for denoting ROOT of AST 
    (for multiple options for root, use ^ ( a | b | c )) 

*   GrammarReader is now its own class, and Rule AST trees get passed to the lexer for 
    non-pre-defined tokens. The next step is to generate recognizers for said tokens
    based on the Rule AST trees for each given token.


*   Re-factor grammar to support operator (mathmatical) precedence. See python grammar for example.
    Add rules like: Factor, term, primary

    DONE. Basic support is there. No support yet for exponets (aka using ** ) but that can come later. 

*   Add support for exponets in expressions
        

*   Test that the parser correctly tells you where syntax errors are occuring (line number and char position)