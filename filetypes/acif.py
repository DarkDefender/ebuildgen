from ply import lex
from ply import yacc

def parseif(ifoptions):
    optstr = ""
    for option in ifoptions:
        optstr += option + " "

    tokens = (
            "NOT",
            "AND",
            "OR",
            "EQ",
            "NEQ",
            "NONZERO",
            "SEMICOL",
            "LBRAC",
            "RPRAC",
            "OPT",
            "TEST",
            )

    def t_TEST(t):
        r"test"
        return t

    def t_AND(t):
        r"(\-a|\&\&)"
        return t

    def t_OR(t):
        r"(\-o|\|\|)"
        return t

    def t_EQ(t):
        r"="
        return t

    def t_NEQ(t):
        r"\!="
        return t

    def t_NOT(t):
        r"\!"
        return t

    def t_NONZERO(t):
        r"\-n"
        return t

    def t_SEMICOL(t):
        r";"
        pass

    def t_LBRAC(t):
        r"\{"
        return t

    def t_RPRAC(t):
        r"\}"
        return t

    def t_space(t):
        r"[ \t\n]"
        pass

    def t_quote(t):
        r"[\"\']"
        pass

    def t_OPT(t):
        r"[^ \t\n;\"\']+"
        return t

    def t_ANY_error(t):
        print("Illegal character '%s'" % t.value[0],t.lexer.lineno)
        t.lexer.skip(1)

    lexer = lex.lex()

    #lexer.input(optstr)
    #for tok in lexer:
    #    print(tok)

    #YACC
    #Add more cases!

    def p_exp(p):
        """
        exp : NOT TEST expopt
            | TEST expopt
        """
        if len(p) == 4:
            newlst = []
            while len(newlst) < len(p[3]):
                if p[3][len(newlst)+1][0] == "!":
                    newresult = p[3][len(newlst)+1][1:]
                else:
                    newresult = "!" + p[3][len(newlst)+1]

                newlst += [p[3][len(newlst)],newresult]

            p[0] = newlst

        else:
            p[0] = p[2]

    def p_expopt(p):
        """
        expopt : expopt AND expopt
               | expopt OR expopt
        """
        if p[2] == "-a":
            p[0] = p[1] + p[3]
        else:  #come up with something better
            p[0] = p[1] + p[3]

    def p_expopt2(p):
        """
        expopt : OPT EQ OPT
               | OPT NEQ OPT
               | NONZERO OPT
               | OPT
        """
        if len(p) == 4:
            if p[2] == "=":
                varstr = p[1].split("$")
                p[0] = [varstr[1],p[3][len(varstr[0]):]]
                #[VARIABLEname,value to pass test]

            elif p[2] == "!=":
                varstr = p[1].split("$")
                p[0] = [varstr[1],"!" + p[3][len(varstr[0]):]]

        else:
            varstr = p[len(p)-1].split("$")[1]
            p[0] = [varstr, "!"] #req that the variable is nonzero to be True

    def p_error(p):
        print("syntax error at '%s'" % p.type,p.value)
        pass

    yacc.yacc()
    return yacc.parse(optstr)

