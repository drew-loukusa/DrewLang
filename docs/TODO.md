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