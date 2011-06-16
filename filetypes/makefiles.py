from ply import lex
from ply import yacc
from makefilecom import expand

def scanmakefile(makefile):
    tokens = (
            "VAR",
            "DOTVAR",
            "END",
            "COL",
            "SEMICOL",
            "EQ",
            "PEQ",
            "CEQ",
            "QEQ",
            "TEXT",
            "COMMAND",
            "PERCENT",
            "ENDTAB",
            "LIT",
            "COMMA",
            )

    states = (
            ("com", "exclusive"),
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

    def t_begin_com(t):
        r"\#"
        t.lexer.push_state("com")

    def t_com_other(t):
        r"[^(\n|\\)]+"
        pass

    def t_com_newline(t):
        r".*\\\n"
        t.lexer.lineno += 1
        pass

    def t_com_END(t):
        r"\n"
        t.lexer.pop_state()
        t.lexer.lineno += 1
        return t

    def t_EQ(t):
        r"="
        return t

    def t_COL(t):
        r":"
        return t

    def t_SEMICOL(t):
        r";"
        return t

    def t_bsdexe(t):  #Create a cleaner version
        r".*\!=.*"
        pass

    def t_PERCENT(t):
        r"\%"
        return t

    def t_PEQ(t):
        r"[a-zA-Z_][a-zA-Z0-9_]*[ \t]*\+="
        t.value = t.value.split()[0].rstrip("+=")
        return t

    def t_CEQ(t):
        r"[a-zA-Z_][a-zA-Z0-9_]*[ \t]*:="
        t.value = t.value.split()[0].rstrip(":=")
        return t

    def t_QEQ(t):
        r"[a-zA-Z_][a-zA-Z0-9_]*[ \t]*\?="
        t.value = t.value.split()[0].rstrip("?=")
        return t

    def t_VAR(t):
        r"[a-zA-Z_][a-zA-Z0-9_]*[ \t]*="
        t.value = t.value.split()[0].rstrip("=") #get the name of the var
        return t

    def t_DOTVAR(t):
        r"\.[a-zA-Z_][a-zA-Z0-9_]*[ \t]*="
        t.value = t.value.split()[0].rstrip("=") #get the name of the var
        return t

    def t_contline(t):
        r"\\\n"
        t.lexer.lineno += 1
        pass

    def t_LIT(t):
        r"\\."
        t.value = t.value[1] #take the literal char
        return t

    def t_COMMA(t):
        r","
        return t

    def t_spacetab(t):
        r"[ \t]"
        pass

    def t_ENDTAB(t):
        r"\n\t"
        t.lexer.lineno += 1
        return t

    def t_TEXT(t):
        r"[^ \n\t:\\,]+"
        return t

    def t_END(t):
        r"\n+"
        t.lexer.lineno += t.value.count('\n')
        return t

    def t_ANY_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    lexer = lex.lex()

    lexer.input(makefile)
    for tok in lexer:
        print(tok)


    #YACC begins here

    #a dict with values of defined variables
    variables = {}
    ivars = [] #keep track of the immediate variables
    targets = [] #buildtargets, [[target,deps,options],[target2,....

    def p_target(p):

    def p_peq(p): #immediate if peq was defined as immediate before else deferred
        """
        end : end PEQ textlst end
            | PEQ textlst end
        """
        if len(p) == 4:
            if not p[1] in variables:
                variables[p[1]] = p[2]
            elif not p[1] in ivars:
                variables[p[1]] += p[2]
            else:
                textvalue = expand(p[2]) #expand any variables
                variables[p[1]] = textvalue

        elif not p[2] in variables:
            variables[p[2]] = p[3]
        elif not p[2] in ivars:
            variables[p[2]] += p[3]
        else:
            textvalue = expand(p[3]) #expand any variables
            variables[p[2]] = textvalue

    def p_ceq(p): #immediate
        """
        end : end CEQ textlst end
            | CEQ textlst end
        """
        if len(p) == 4:
            textvalue = expand(p[2]) #expand any variables
            variables[p[1]] = textvalue
            ivars.append(p[1])
        else:
            textvalue = expand(p[3]) #expand any variables
            variables[p[2]] = textvalue
            ivars.append(p[2])

    def p_qeq(p): #deferred
        """
        end : end QEQ textlst end
            | QEQ textlst end
        """
        if len(p) == 4 and not p[1] in variables:
            variables[p[1]] = p[2]
        elif not p[2] in variables:
            variables[p[2]] = p[3]

    def p_var(p): #deferred
        """
        end : end VAR textlst end
            | VAR textlst end
        """
        if len(p) == 4:
            variables[p[1]] = p[2]
        else:
            variables[p[2]] = p[3]

    def p_textlst(p):
        """
        textlst : textlst TEXT
                | textlst command
                | textlst LIT
                | command
                | TEXT
                | LIT
        """
        if len(p) == 3:
            p[0] = p[1].append(p[2])
        else:
            p[0] = [p[1]]

    def p_command(p):
        "command: COMMAND"
        p[0] = [p[1]] #commands are lists within the testlst

    def p_end(p):
        """
        end : END
            | end END
        """

    def p_error(p):
        print("syntax error at '%s'" % p.type,p.lexpos)
        pass

    #yacc.yacc()

    #yacc.parse(makefile)

    #for target in targets:
    #    print(target)
    #print(variables)

    #return targets


#immediate
#deferred


file="Makefile2"

with open(file, encoding="utf-8", errors="replace") as inputfile:
    scanmakefile(inputfile.read())
