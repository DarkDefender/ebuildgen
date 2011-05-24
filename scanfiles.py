import os
import glob
from ply import lex
from ply import yacc

def scandir(dir, filetypes):
    files = []
    dirs = [f for f in os.listdir(dir)
        if os.path.isdir(os.path.join(dir, f))]
    for dir_path in dirs:
        files += scandir(dir + "/" + dir_path, filetypes)
    for filetype in filetypes:
        files += glob.glob(dir + "/*" + filetype)
    return files

#lex stuff begins here

def scanincludes(string,inclst):
    tokens = (
            "GINCLUDE",
            "LINCLUDE",
            "BUNDLEINC",
            "IFDEF",
            "ENDIF",
            )

    states = (
            ("com","exclusive"), #comment
            ("ifdef","inclusive"),
            )

    t_ANY_ignore = " \t"

    def t_begin_com(t):
        r"/\*"
        t.lexer.push_state("com")

    def t_com_end(t):
        r"\*/"
        t.lexer.pop_state()
        pass

    def t_line_com(t):
        r"//.*"
        pass

    def t_ANY_begin_if0(t):
        r"\#if[ \t]+0"
        t.lexer.push_state("com")

    def t_com_endif(t):
        r"\#endif"
        t.lexer.pop_state()
        pass

    def t_com_ifdef(t):
        r"\#ifdef"
        t.lexer.push_state("com")

    def t_IFDEF(t):
        r"\#ifdef[ \t]+[a-zA-Z_][a-zA-Z0-9_]*"
        t.value = t.value[6:].strip() #return the ifdef name
        t.lexer.push_state("ifdef")
        return t

    def t_ifdef_ENDIF(t):
        r"\#endif"
        t.lexer.pop_state()
        return t

    def t_GINCLUDE(t):
        r"\#[Ii][Nn][Cc][Ll][Uu][Dd][Ee][ \t]+<.*\.h>"
        t.value = t.value[8:].strip().strip("<>")
        return t

    def t_LINCLUDE(t):
        r"\#[Ii][Nn][Cc][Ll][Uu][Dd][Ee][ \t]+\".*\.h\""
        t.value = t.value[8:].strip().strip('""')
        return t

    def t_BUNDLEINC(t):
        r"\#[Ii][Nn][Cc][Ll][Uu][Dd][Ee][ \t]+<.*>"
        pass

    def t_ANY_error(t):
        #print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    lexer = lex.lex()

    #lexer.input(string)
    #
    #for tok in lexer:
    #    print(tok)
    #
    #YACC stuff here

    def p_includes2(p):
        """
        includes : includes ginc
                 | includes linc
                 | includes IFDEF includes ENDIF
                 | IFDEF includes ENDIF
        """

    def p_includes(p):
        """
        includes : ginc
                 | linc
        """

    def p_ginclude(p):
        "ginc : GINCLUDE"
        inclst[0].add(p[1])

    def p_linclude(p):
        "linc : LINCLUDE"
        inclst[1].add(p[1])

    def p_error(p):
        print("syntax error at '%s'" % p.value)
        pass

    yacc.yacc()

    yacc.parse(string)
    return(inclst)


def startscan(dir,filetypes):
    global_hfiles = set()
    local_hfiles = set()
    inclst = [global_hfiles,local_hfiles]

    for file in scandir(dir, filetypes):
        print(file)

        with open(file, encoding="utf-8", errors="replace") as inputfile:
            inclst = scanincludes(inputfile.read(),inclst)

    return(inclst)

