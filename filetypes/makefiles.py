from ply import lex
from ply import yacc
from makefilecom import expand

def scanmakefile(makefile):
    makefile = "\n" + makefile #Add \n so you can guess vars
    tokens = (
            "END",
            "COL",
            "SEMICOL",
            "EQ",
            "PEQ",
            "CEQ",
            "QEQ",
            "TEXT",
            "COMMAND",
            "ENDTAB",
            "LIT",
            "SPACE",
            )

    states = (
            ("com", "exclusive"),
            ("ccode", "exclusive"), #command code
            ("var", "inclusive"),
            )

    # Match the first $(. Enter ccode state.
    def t_ccode(t):
        r'\$(\{|\()'
        t.lexer.code_start = t.lexer.lexpos        # Record the starting position
        t.lexer.level = 1                          # Initial level
        t.lexer.push_state('ccode')                     # Enter 'ccode' state

    # Rules for the ccode state
    def t_ccode_newcom(t):
        r'\$(\{|\()'
        t.lexer.level +=1

    def t_ccode_endcom(t):
        r'(\}|\))'
        t.lexer.level -=1

        # If closing command, return the code fragment
        if t.lexer.level == 0:
             t.value = t.lexer.lexdata[t.lexer.code_start-1:t.lexer.lexpos]
             t.type = "COMMAND"
             t.lexer.pop_state()
             return t

    def t_ccode_text(t):
        r"[^\$\(\{\)\}]"

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

    def t_com_END(t):
        r"\n"
        t.lexer.begin("INITIAL")
        t.lexer.lineno += 1
        return t

    def t_bsdexe(t):  #Create a cleaner version
        r".*\!=.*"
        pass

    def t_EQ(t):
        r"[ \t]*=[ \t]*"
        t.lexer.begin("var")
        return t

    def t_PEQ(t):
        r"[ \t]*\+=[ \t]*"
        t.lexer.begin("var")
        return t

    def t_CEQ(t):
        r"[ \t]*:=[ \t]*"
        t.lexer.begin("var")
        return t

    def t_QEQ(t):
        r"[ \t]*\?=[ \t]*"
        t.lexer.begin("var")
        return t

    def t_contline(t):
        r"\\\n"
        t.lexer.lineno += 1
        pass

    def t_LIT(t):
        r"\\."
        t.value = t.value[1] #take the literal char
        return t

    def t_COL(t):
        r"[ \t]*:[ \t]*"
        t.lexer.begin("var")
        return t

    def t_var_ENDTAB(t):
        r"[ \t]*;[ \t]*"
        return t

    def t_SEMICOL(t):
        r";"
        return t

    def t_COMMA(t):
        r","
        return t

    def t_ENDTAB(t):
        r"[ \t]*\n\t[ \t]*"
        t.lexer.lineno += 1
        return t

    def t_var_TEXT(t):
        r"[^ #\n\t,\$\\]+"
        return t

    def t_TEXT(t):
        r"[^ \n\t:\?\+=\\,\$]+"
        return t

    def t_END(t):
        r"[ \t]*\n+"
        t.lexer.lineno += t.value.count('\n')
        t.lexer.begin('INITIAL')
        return t

    def t_SPACE(t):
        r"[ \t]"
        return t

    def t_var_special(t):
        r"\$[^({]"
        t.type = "TEXT"
        return t

    def t_ANY_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    lexer = lex.lex()

    #lexer.input(makefile)
    #for tok in lexer:
    #    print(tok)

    #YACC begins here

    #a dict with values of defined variables
    variables = {}
    ivars = [] #keep track of the immediate variables
    targets = [] #buildtargets, [[target,deps,options],[target2,....

    def p_testvar(p):
        """
        comp : comp var
             | comp rule
             | comp end
             | var
             | rule
        """

    def p_ruleoption(p):
        """
        rule : end textlst COL textlst options
             | end textlst COL options
        """
        if len(p) == 6:
            for target in expand(p[2],variables):
                targets.append([target,expand(p[4],variables),p[5]])
        else:
            for target in expand(p[2],variables):
                targets.append([target,[],p[4]])

    def p_rule(p):
        """
        rule : end textlst COL textlst
             | end textlst COL
        """
        if len(p) == 5:
            for target in expand(p[2],variables):
                targets.append([target,expand(p[4],variables),[]])
        else:
            for target in expand(p[2],variables):
                targets.append([target,[],[]])

    def p_peq(p): #immediate if peq was defined as immediate before else deferred
        """
        var : end textstr PEQ textlst
            | end textstr PEQ
        """
        if len(p) == 5:
            if not p[2] in variables:
                variables[p[2]] = p[4]
            elif not p[2] in ivars:
                variables[p[2]] += p[4]
            else:
                textvalue = expand(p[4],variables) #expand any variables
                variables[p[2]] = textvalue

    def p_ceq(p): #immediate
        """
        var : end textstr CEQ textlst
            | end textstr CEQ
        """
        if len(p) == 5:
            textvalue = expand(p[4],variables) #expand any variables
            variables[p[2]] = textvalue
            ivars.append(p[2])
        else:
            variables[p[2]] = []
            ivars.append(p[2])

    def p_qeq(p): #deferred
        """
        var : end textstr QEQ textlst
            | end textstr QEQ
        """
        if not p[2] in variables and len(p) == 5:
            variables[p[2]] = p[4]
        else:
            variables[p[2]] = []

    def p_var(p): #deferred
        """
        var : end textstr EQ textlst
            | end textstr EQ
        """
        if len(p) == 5:
            variables[p[2]] = p[4]
        else:
            variables[p[2]] = []

    def p_options(p):
        """
        options : options ENDTAB textlst
                | ENDTAB textlst
        """
        if len(p) == 4:
            p[0] = p[1] + p[3]
        else:
            p[0] = p[2]

    def p_textlst(p):
        """
        textlst : textlst spacestr command
                | textlst spacestr textstr
                | command
                | textstr
        """
        if len(p) == 4:
            p[0] = p[1]+ [p[3]]
        else:
            p[0] = [p[1]]

    def p_com_and_str(p):
        """
        command : command textstr
                | textstr command
        """
        if isinstance(p[1],list):
            p[0] = [p[1][0] + p[2]]
        else:
            p[0] = [p[1] + p[2][0]]

    def p_textstr(p):
        """
        textstr : textstr LIT
                | textstr TEXT
                | TEXT
                | LIT
        """
        if len(p) == 3:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1]

    def p_command(p):
        """
        command : command COMMAND
                | COMMAND
        """
        if len(p) == 2:
            p[0] = [p[1]] #commands are lists within the textlst
        else:
            p[0] = [p[1][0] + p[2]]

    def p_space(p):
        """
        spacestr : spacestr SPACE
                 | SPACE
        """
        if len(p) == 3:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1]

    def p_end(p):
        """
        end : end END
            | end spacestr END
            | END
        """


    def p_error(p):
        print("syntax error at '%s'" % p.type,p.lexpos)
        pass

    yacc.yacc()

    yacc.parse(makefile)

    for target in targets:
        print(target)
    print(variables)

    #return targets


#immediate
#deferred


file="Makefile"

with open(file, encoding="utf-8", errors="replace") as inputfile:
    scanmakefile(inputfile.read())
