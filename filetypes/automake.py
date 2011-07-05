from ply import lex
from ply import yacc
import glob

def scanamfile(amfile):
    """Scan automake (.am) file

    Returns ...
    """
    amfile = "\n" + amfile #Add \n so you can guess vars
    tokens = (
            "END",
            "COL",
            "EQ",
            "PEQ",
            "CVAR",
            "MVAR",
            "TEXT",
            "ENDTAB",
            "SPACE",
            )

    states = (
            ("com", "exclusive"), #comment
            ("var", "inclusive"),
            )

    def t_begin_com(t):
        r"[ \t]*\#"
        t.lexer.begin("com")

    def t_com_other(t):
        r"[^\\\n]+"
        pass

    def t_com_lit(t):
        r"\\."
        pass

    def t_com_newline(t):
        r".*\\\n"
        t.lexer.lineno += 1
        pass

    def t_CVAR(t): #configure variable
        r"@.*?@" #not greedy
        t.value = t.value.strip("@")
        return t

    def t_MVAR(t): #makefile variable
        r"\$\(.*?\)"
        return t

    def t_com_END(t):
        r"\n"
        t.lexer.begin("INITIAL")
        t.lexer.lineno += 1
        return t

    def t_EQ(t):
        r"[ \t]*=[ \t]*"
        t.lexer.begin("var")
        return t

    def t_PEQ(t):
        r"[ \t]*\+=[ \t]*"
        t.lexer.begin("var")
        return t

    def t_contline(t):
        r"\\\n"
        t.lexer.lineno += 1
        pass

    def t_litteral(t):
        r"\\."
        t.value = t.value[1] #take the literal char
        t.type = "TEXT"
        return t

    def t_COL(t):
        r"[ \t]*:[ \t]*"
        t.lexer.begin("var")
        return t

    def t_var_ENDTAB(t):
        r"[ \t]*;[ \t]*"
        return t

    def t_ENDTAB(t):
        r"[ \t]*\n\t[ \t]*"
        t.lexer.lineno += 1
        return t

    def t_var_TEXT(t):
        r"[^ #\n\t,\$@\\]+"
        return t

    def t_TEXT(t):
        r"[^ \n\t:=\$@\\]+"
        return t

    def t_END(t):
        r"[ \t]*\n+"
        t.lexer.lineno += t.value.count('\n')
        t.lexer.begin('INITIAL')
        return t

    def t_SPACE(t):
        r"[ \t]+"
        return t

    def t_var_special(t):
        r"\$[^({]"
        t.type = "TEXT"
        return t

    def t_ANY_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    lexer = lex.lex()

    #lexer.input(amfile)
    #for tok in lexer:
    #    print(tok)

    #YACC stuff begins here

    def p_done(p):
        "done : vars END"
        p[0] = p[1]

    def p_vars(p):
        """
        vars : vars END var
             | END var
        """
        if len(p) == 4:
            p[1].update(p[3])
            p[0] = p[1]
        else:
            p[0] = p[2]

    def p_var(p):
        """
        var : textstr EQ textlst
            | textstr PEQ textlst
        """
        p[0] = {p[1]:p[3]}

    def p_textlst(p):
        """
        textlst : textlst spacestr textstr
                | textstr
        """
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    def p_teststr(p):
        """
        textstr : textstr TEXT
                | textstr CVAR
                | textstr MVAR
                | TEXT
                | CVAR
                | MVAR
        """
        if len(p) == 3:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1]

    def p_space(p):
        """
        spacestr : spacestr SPACE
                 | SPACE
        """
        if len(p) == 3:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1]

    def p_error(p):
        print("syntax error at '%s'" % p.type,p.value)
        pass

    yacc.yacc()

    variables = yacc.parse(amfile)
    print(variables)

file="/usr/portage/distfiles/svn-src/moc/trunk/Makefile.am"

with open(file, encoding="utf-8", errors="replace") as inputfile:
    scanamfile(inputfile.read()) 
