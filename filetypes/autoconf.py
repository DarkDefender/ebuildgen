from ply import lex
from ply import yacc

def scanacfile(acfile):
    """Scan a autoconfigure (.in/.ac) file.

    Returns ....
    """

    tokens = (
            "FUNC",
            "FUNCOPT", #func options
            "FUNCEND",
            "VAR",
            "ECHO",
            "TEXT",
            "IF",
            "IFCOM",
            "ELSE",
            "THEN",
            "IFEND",
            "CASE",
            "CASEOPT",
            "COPTEND", #case opt end, doesn't need to be there but SHOULD
            "CASEEND",
            )

    states = (
            ("func", "exclusive"),
            ("funcopt", "exclusive"),
            ("case", "inclusive"),
            ("if", "inclusive"),
            )

    def t_ANY_contline(t):
        r"\\\n"
        t.lexer.lineno += 1
        pass

    def t_ANY_space(t):
        r"[ \t]"
        pass

    def t_ANY_newline(t):
        r"\n"
        t.lexer.lineno += 1
        pass

    def t_INITIAL_func_FUNC(t):
        r'[a-zA-Z_][a-zA-Z0-9_]*\('
        t.lexer.push_state('func')
        t.value = t.value[:-1] #return name of func
        return t

    def t_func_funcopt(t):
        r'\['
        t.lexer.code_start = t.lexer.lexpos        # Record the starting position
        t.lexer.level = 1                          # Initial level
        t.lexer.push_state('funcopt')                # Enter 'ccode' state

    # Rules for the ccode state
    def t_funcopt_newcom(t):
        r'\['
        t.lexer.level +=1

    def t_funcopt_endcom(t):
        r'\]'
        t.lexer.level -=1

        # If closing command, return the code fragment
        if t.lexer.level == 0:
             t.value = t.lexer.lexdata[t.lexer.code_start-1:t.lexer.lexpos]
             t.type = "FUNCOPT"
             t.lexer.lineno += t.value.count('\n')
             t.lexer.pop_state()
             return t

    def t_funcopt_opt(t):
        r"[^\\\[\]]+"

    def t_func_FUNCOPT(t):
        r"[^\\\(\)\[\],]+"
        t.lexer.lineno += t.value.count('\n')
        return t

    def t_func_comma(t):
        r"[ \t]*,[ \t]*"
        pass

    def t_func_FUNCEND(t):
        r"\)"
        t.lexer.pop_state()
        return t

    def t_comment(t):
        r"(dnl|\#).*\n"
        t.lexer.lineno += t.value.count('\n')
        pass

    def t_ECHO(t):
        r"echo.*\n"
        t.lexer.lineno += t.value.count('\n')
        return t

    def t_VAR(t):
        r"[a-zA-Z_][a-zA-Z0-9_]*=([^\\\n]|\\\n)*\n"
        return t

    def t_IF(t):
        r"if"
        t.lexer.push_state("if")
        return t

    def t_if_THEN(t):
        r"then"
        t.lexer.pop_state()
        return t

    def t_if_IFCOM(t):
        r"[^ \t\n\(\)]+"
        return t

    def t_ELSE(t):
        r"else"
        return t

    def t_IFEND(t):
        r"fi"
        return t

    def t_CASE(t):
        r"case.*in"
        t.lexer.push_state("case")
        return t

    def t_CASEEND(t):
        r"esac"
        t.lexer.pop_state()
        return t

    def t_case_CASEOPT(t):
        r"[^ \n\t\(\)]+\)"
        return t

    def t_case_COPTEND(t):
        r";;"
        return t

    def t_literal(t):
        r"\\[^\n]"
        t.type = "TEXT"
        t.value = t.value[-1] #return litral char
        return t

    def t_TEXT(t):            #most likely commands like "AM_INIT_AUTOMAKE" etc.
        r"[^ \t\n\(\)]+"
        return t

    def t_ANY_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    lexer = lex.lex()

    lexer.input(acfile)
    for tok in lexer:
        print(tok)

    #YACC stuff begins here

    def p_complst(p):
        """
        complst : complst var
                | complst func
                | var
                | func
        """

    def p_textlst(p):
        """
        textlst : textlst TEXT
                | TEXT
        """
        if len(p) == 3:
            p[0] = p[1] += [p[1]]
        else:
            p[0] = [p[1]]

file="configure.in"

with open(file, encoding="utf-8", errors="replace") as inputfile:
    scanacfile(inputfile.read())
