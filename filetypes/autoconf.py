from ply import lex
from ply import yacc

def scanacfile(acfile):

    tokens = (
            "FUNC",
            "FUNCOPT", #func options
            "FUNCEND",
            "VAR",
            "ECHO",
            "TEXT",
            "IF",
            "ELSE",
            "THEN",
            "IFEND",
            "CASE",
            "CASEEND",
            )

    states = (
            ("func", "exclusive"),
            ("funcopt", "exclusive"),
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
        return t

    def t_THEN(t):
        r"then"
        return t

    def t_ELSE(t):
        r"else"
        return t

    def t_IFEND(t):
        r"fi"
        return t

    def t_CASE(t):
        r"case.*in"
        return t

    def t_CASEEND(t):
        r"esac"
        return t

    def t_literal(t):
        r"\\[^\n]"
        t.type = "TEXT"
        t.value = t.value[-1] #return litral char
        return t

    def t_TEXT(t):
        r"[^ \t\n\(\)]+"
        return t

    def t_ANY_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    lexer = lex.lex()

    lexer.input(acfile)
    for tok in lexer:
        print(tok)

file="configure.in"

with open(file, encoding="utf-8", errors="replace") as inputfile:
    scanacfile(inputfile.read())
