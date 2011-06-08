from ply import lex
from ply import yacc

def scanmakefile(makefile):
    tokens = (
            "VAR",
            "COLON",
            "PERCENT",
            "TEXT",
            "DOLLAR",
            "LPAR",
            "RPAR",
            "END",
            "EQUAL",
            "ENDTAB",
            "LESS",
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

    def t_VAR(t):
        r"[a-zA-Z_][a-zA-Z0-9_]*[ \t]*="
        t.value = t.value.split()[0].rstrip("=") #get the name of the var
        return t

    def t_TEXT(t):
        #make sure it grabs "file-name" and "-flags"
        r"-*\.*[a-zA-Z_][-|a-zA-Z0-9_]*"
        return t

    def t_LESS(t):
        r"\$<"
        pass

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

    def t_contline(t):
        r"\\\n"
        pass

    def t_ENDTAB(t):
        r"\n\t"
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
    targets = [] #buildtargets, [[target,deps,options],[target2,....

    def p_target(p):
        """
        var : var textlst COLON textlst end
            | textlst COLON textlst end
            | var textlst COLON textlst options end
            | textlst COLON textlst options end
        """
        if len(p) == 6:
            if p[3] == ":":
                targets.append([p[2][0],p[4],[]])
            else:
                targets.append([p[1][0],p[3],p[4]])
        elif len(p) == 5:
            targets.append([p[1][0],p[3],[]])
        else:
            targets.append([p[2][0],p[4],p[5]])

    def p_lonetarget(p):
        """
        var : var textlst COLON options end
            | textlst COLON options end
        """
        if len(p) == 6:
            targets.append([p[2][0],[],p[4]])
        else:
            targets.append([p[1][0],[],p[3]])

    def p_depconv(p):
        """
        var : var command COLON command end
            | var command COLON command options end
        """
        if len(p) == 6:
            options = []
        else:
            options = p[5]

        if p[2][0] == p[4][0] == "%":
            for target in targets:
                for dep in target[1]:
                    if p[2][1] in dep:
                        targets.append([dep,[(dep.replace(p[2][1],p[4][1]))],options])
        else:
            print("Unknown command")

    def p_var(p):
        """
        var : VAR textlst end
            | VAR end
            | var VAR textlst end
            | var VAR end
        """
        if isinstance(p[2],list):
            variables[p[1]] = p[2]
        elif len(p) == 5:
            variables[p[2]] = p[3]
        elif len(p) == 3:
            variables[p[1]] = []
        else:
            variables[p[2]] = []

    def p_endtab(p):
        """
        options : ENDTAB textlst
                | options ENDTAB textlst
        """
        if len(p) == 3:
            p[0] = p[2]
        else:
            p[0] = p[1] + p[3]

    def p_usecom(p):
        """
        textlst : DOLLAR LPAR textlst COLON command RPAR
                | textlst DOLLAR LPAR textlst COLON command RPAR
        """
        if len(p) == 8:
            o = 1 #offset
        else:
            o = 0
        p[3+o] = variables[p[3+o][0]]
        p[0] = []
        if p[5][0] == "replace":
            for text in p[3+o]:
                p[0] += [text.replace(p[5+o][1],p[5+o][2])]
        else:
            for text in p[3+o]:
                p[0] += [text + p[5+o][1]]

    def p_textlst(p):
        """
        textlst : textlst TEXT
                | TEXT
                | DOLLAR LPAR textlst RPAR
                | textlst DOLLAR LPAR textlst RPAR
        """
        if len(p) == 2:
            p[0] = [p[1]]
        elif len(p) == 3:
            p[0] = p[1] + [p[2]]
        elif len(p) == 5:
            if p[3][0] in variables:
                var = variables[p[3][0]]
                p[0] = var
            else:
                p[0] = ["not defined"]
        else:
            if p[4][0] in variables:
                var = variables[p[4][0]]
                p[0] = p[1] + var
            else:
                p[0] = ["not defined"]

    def p_command(p):
        """
        command : TEXT EQUAL TEXT
                | PERCENT EQUAL PERCENT TEXT
                | PERCENT TEXT
        """
        if len(p) == 4:
            p[0] = ["replace", p[1], p[3]]
        elif len(p) == 5:
            p[0] = ["append", p[4]]
        else:
            p[0] = [p[1],p[2]]

    def p_end(p):
        """
        end : end END
            | END
        """

    def p_error(p):
        print("syntax error at '%s'" % p.type,p.lexpos)
        pass

    yacc.yacc()

    yacc.parse(makefile)

    #for target in targets:
    #    print(target)
    #print(variables)

    return targets

