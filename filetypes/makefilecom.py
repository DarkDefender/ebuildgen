from ply import lex
from ply import yacc

def com_interp(string):
    tokens = (
            "COMMAND",
            "COMMA",
            "EQ",
            "TEXT",
            "PERCENT",
            )
    states = (
            ("ccode", "exclusive"), #command code
            )

    # Match the first $(. Enter ccode state.
    def t_ccode(t):
        r'\$(\{|\()'
        t.lexer.code_start = t.lexer.lexpos        # Record the starting position
        t.lexer.level = 1                          # Initial level
        t.lexer.begin('ccode')                     # Enter 'ccode' state

    # Rules for the ccode state
    def t_ccode_newcom(t):
        r'\$(\{|\()'
        t.lexer.level +=1

    def t_ccode_endcom(t):
        r'(\}|\))'
        t.lexer.level -=1

        # If closing command, return the code fragment
        if t.lexer.level == 0:
             t.value = t.lexer.lexdata[t.lexer.code_start:t.lexer.lexpos-1]
             t.type = "COMMAND"
             t.lexer.begin('INITIAL')
             return t

    def t_ccode_text(t):
        "[^\$\(\{\)\}]"

    def t_PERCENT(t):
        r"\%"
        return t

    def t_EQ(t):
        r"="
        return t 

    def t_COMMA(t):
        r","
        return t

    def t_TEXT(t):
        r"[^ \n\t:=\\,]+"
        return t

    def t_spacetab(t):
        r"[ \t]"
        pass

    def t_ANY_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    lexer = lex.lex()

    lexer.input(string)
    #for tok in lexer:
    #    print(tok)

    tokens = 0
    for tok in lexer:
        tokens += 1
        print("gethere")

    print(tokens)
    if tokens == 1:
        print("gapp")


com_interp("HELOO")
