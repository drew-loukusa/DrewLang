if __name__ == "__main__":
    import os 
    import sys
    input = \
"""x=0;
print("Helloworld");
if(x==0){
    print("xis0");
    print(x);
    x=1;
}
"""

    cwd = os.getcwd()[0:-8]
    #drewparser = Parser(input, 2, cwd + "\\docs\\grammar_grammar.txt") 
    drewparser = Parser(input, 2, cwd + "\\docs\\DrewGrammar.txt")
    AST = drewparser.program()
    AST.toStringTree()