AST Todo:

*   I have decided on a format for describing the AST structure in my grammar. It's essentially the ANTLR format, but             _slightly_ changed. Now I need to do the following:

*   Figure out how to handle no root node being set: See expr. 

        Root is add_op for expr, but add_op is optional.
        What code will I generate to handle that? (No root node)

*   Handle embedding ^ into normal rule defs. 

        Will have to make generator ignore ';' and '{' and other non-ast things to support that style of AST def.

*   Handle ' -> ^( ast def ) ' 

        Will have to make changes to _bulid_rules_from_RuleTokens() to accomodate this new change.

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