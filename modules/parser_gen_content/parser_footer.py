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
    from locate_file import check_cache_or_find
    # Get path to grammar file: 
    grammar_file_name = "DrewGrammar.txt"
    grammar_file_path = check_cache_or_find(grammar_file_name, start_dir="C:\\Users", path_cache_file="paths.txt")

    cwd = os.getcwd()[0:-8]
    #drewparser = Parser(input, 2, grammar_file_path) 
    drewparser = Parser(input, 2, grammar_file_path)
    AST = drewparser.program()
    AST.toStringTree()