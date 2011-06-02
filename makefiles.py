import os
from ply import lex
from ply import yacc

def scanmakefile(makefile):
    tokens = (
            "VARS",
            "COLON",
            "PERCENT",
            "TEXT",
            "DOLLAR",
            "LPAR",
            "RPAR",
            "CONTLINE",
            "END",
            "EQUAL",
            "INCLUDEFLAG"
            )

    states = (
            ("com", "exclusive"),
            )

    def t_begin_com(t):
        r"\#"
        t.lexer.push_state("com")

    def t_com_newline(t):
        r".*\\[ \t]*\n"
        pass

    def t_com_END(t):
        r"\n"
        t.lexer.pop_state()
        return t

    def t_INCLUDEFLAG(t):
        r"-I"
        return t

    def t_VARS(t):
        r"[a-zA-Z_][a-zA-Z0-9_]*[ \t]*="
        t.value = t.value.split()[0].rstrip("=") #get the name of the var
        return t

    def t_TEXT(t):
        #make sure it grabs "file-name" and "-flags"
        r"-*\.*[a-zA-Z_][-|a-zA-Z0-9_]*"
        return t

    def t_DOLLAR(t):
        r"\$"
        return t

    def t_COLON(t):
        r"\:"
        return t

    def t_EQUAL(t):
        r"\="
        return t

    def t_LPAR(t):
        r"\("
        return t

    def t_RPAR(t):
        r"\)"
        return t

    def t_PERCENT(t):
        r"\%"
        return t

    def t_CONTLINE(t):
        r"\\"
        return t

    def t_END(t):
        r"[\n]+"
        return t

    def t_ANY_error(t):
        t.lexer.skip(1)

    lexer = lex.lex()

    #lexer.input(makefile)
    #for tok in lexer:
    #    print(tok)


    #YACC begins here

    #a dict with values of defined variables
    variables = {}

    def p_sumfiles(p):
        "files : files sourcefiles"
        p[0] = p[1] + p[2]

    def p_files(p):
        "files : sourcefiles"
        p[0] = p[1] + p[2]

    def p_var(p):
        "var : VARS textlst END"

    def p_textlst(p):
        """
        textlst : textlst TEXT
                | TEXT
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]



file = "/usr/portage/distfiles/svn-src/doneyet-read-only/trunk/Makefile"

with open(file, encoding="utf-8", errors="replace") as inputfile:
    scanmakefile(inputfile.read())

