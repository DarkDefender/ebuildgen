from ply import lex
from ply import yacc
import glob
import os
from subprocess import getstatusoutput

def expand(lst,variables):
    """Expands makefile variables.

    Expand all items in the supplied list that are list within the list.
    Returns a list where all the previously unexpanded variables are now
    expanded.
    Besides the list this needs a dict with variables found in the makefile.
    """

    newlst = []
    for item in lst:
        if isinstance(item, list):
            strlst = com_interp(item[0],variables)
            newlst += expand(strlst,variables)
        else:
            newlst.append(item)

    return newlst

def com_interp(string,variables):
    """Interpret the supplied command and return a list with the output

    """

    tokens = (
            "COMMAND",
            "COMMA",
            "COL",
            "EQ",
            "TEXT",
            "PERCENT",
            "BEGINCOM",
            "ENDCOM",
            "SPACE",
            )
    states = (
            ("ccode", "exclusive"), #command code
            ("eval", "exclusive"), #code to evaluate
            )

    # Match the first $(. Enter ccode state.
    def t_eval_ccode(t):
        r'\$(\{|\()'
        t.lexer.code_start = t.lexer.lexpos        # Record the starting position
        t.lexer.level = 1                          # Initial level
        t.lexer.push_state('ccode')                # Enter 'ccode' state

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

    def t_BEGINCOM(t):
        r"(\(|\{)"
        t.lexer.begin("eval")
        return t

    def t_eval_ENDCOM(t):
        r"(\)|\})"
        t.lexer.begin("INITIAL")
        return t

    def t_eval_PERCENT(t):
        r"\%"
        return t

    def t_eval_EQ(t):
        r"="
        return t

    def t_eval_COMMA(t):
        r",[ \t]*"
        return t

    def t_eval_COL(t):
        r":"
        return t

    def t_eval_TEXT(t):
        r"[^ \n\t:=\)\}\(\}\\\$,]+"
        return t

    def t_TEXT(t):
        r"[^ \t$\(\{]"
        return t

    def t_ANY_SPACE(t):
        r"[ \t]"
        return t

    def t_ANY_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    lexer = lex.lex()

    #lexer.input(string)
    #for tok in lexer:
    #    print(tok)


    #YACC stuff begins here

    def p_comp(p):
        """
        complst : BEGINCOM newstr ENDCOM
                | func
        """
        if len(p) == 4:
            p[0] = p[2]
        else:
            p[0] = p[1]

    def p_complst(p):
        "complst : compstr"
        p[0] = p[1].split()

    def p_compstr(p):
        """
        compstr : compstr BEGINCOM textstr ENDCOM
                | BEGINCOM textstr ENDCOM
                | compstr textstr
                | compstr spacestr
                | textstr
                | spacestr
        """
        p[0] = ""
        if len(p) == 4:
            if p[2] in variables:
                for item in expand(variables[p[2]],variables):
                    p[0] += item + " "
                p[0] = p[0][:-1]
            else:
                p[0] = ""
        elif len(p) == 5:
            if p[3] in variables:
                for item in expand(variables[p[3]],variables):
                    p[1] += item + " "
                    p[0] = p[1][:-1]
            else:
                p[0] = ""
        elif len(p) == 3:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1]

    def p_tonewstr(p):
        """
        newstr  : getstr EQ textstr PERCENT textstr
                | getstr EQ PERCENT textstr
                | getstr EQ textstr PERCENT
                | getstr EQ PERCENT
                | getstr EQ textstr
        """
        newtextlist = []
        if p[1] == []:
            p[0] = p[1]
        elif len(p) == 6:
            for text in p[1]:
                newtextlist.append(p[3] + text + p[5])
            p[0] = newtextlist

        elif len(p) == 5:
            if p[3] == "%":
                for text in p[1]:
                    newtextlist.append(text + p[4])
                p[0] = newtextlist
            else:
                for text in p[1]:
                    newtextlist.append(p[3] + text)
                p[0] = newtextlist

        elif p[3] == "%":
            p[0] = p[1]
        else:
            for text in p[1]:
                newtextlist.append(text + p[3])
            p[0] = newtextlist


    def p_getstr(p):
        """
        getstr : textstr COL textstr PERCENT textstr
               | textstr COL PERCENT textstr
               | textstr COL textstr PERCENT
               | textstr COL PERCENT
               | textstr COL textstr
        """
        if not p[1] in variables:
            p[0] = []
        else:
            textlst = expand(variables[p[1]],variables) #make sure it's expanded
            newtextlst = []

            if len(p) == 6:
                l1 = len(p[3]) #length of str1
                l2 = len(p[5])
                for text in textlst:
                    if p[3] == text[0:l1] and p[5] == text[-l2:]:
                        newtextlst.append(text[l1:-l2])

                p[0] = newtextlst

            elif len(p) == 5:
                if p[3] == "%":
                    l1 = len(p[4])
                    for text in textlst:
                        if p[4] == text[-l1:]:
                            newtextlst.append(text[:-l1])

                    p[0] = newtextlst
                else:
                    l1 = len(p[3])
                    for text in textlst:
                        if p[3] == text[0:l1]:
                            newtextlst.append(text[l1:])

                    p[0] = newtextlst
            elif p[3] == "%":
                p[0] = textlst
            else:
                l1 = len(p[3])
                for text in textlst:
                    if p[3] == text[-l1:]:
                        newtextlst.append(text[:-l1])

                p[0] = newtextlst

    def p_func(p):
        """
        func : BEGINCOM textstr SPACE funcinput
        """
        #result = ["This calls a function"]
        result = funcdict[p[2]](p[4],variables)
        p[0] = result

    def p_funcinput(p):
        """
        funcinput : funcinput inputstr COMMA
                  | funcinput inputstr ENDCOM
                  | inputstr COMMA
                  | inputstr ENDCOM
        """
        if len(p) == 4:
            if "(" in p[2]: #command in the str
                p[1].append([p[2]])
            else:
                p[1].append(p[2])
            p[0] = p[1]
        else:
            if "(" in p[1]:
                p[0] = [[p[1]]]
            else:
                p[0] = [p[1]]

    def p_inputstr(p):
        """
        inputstr : inputstr spacestr
                 | inputstr TEXT
                 | inputstr COMMAND
                 | spacestr
                 | TEXT
                 | COMMAND
        """
        if len(p) == 3:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1]

    def p_command(p):
        """
        textstr : textstr COMMAND
                | COMMAND
        """
        if len(p) == 3:
            for item in com_interp(p[2],variables):
                p[1] += item + " "
            p[0] = p[1][:-1]
        else:
            p[0] = ""
            for item in com_interp(p[1],variables):
                p[0] += item + " "
            p[0] = p[0][:-1] #remove the last space

    def p_textstr(p):
        """
        textstr : textstr TEXT
                | TEXT
        """
        if len(p) == 3:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1]

    def p_spacestr(p):
        """
        spacestr : spacestr SPACE
                 | SPACE
        """
        if len(p) == 3:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1]

    def p_error(p):
        print("syntax error at '%s'" % p.type,p.lexpos)
        pass

    yacc.yacc()

    retlst = yacc.parse(string)

    #print(retlst)

    return retlst

def foreach(inputlst,variables):
    """GNU makefile foreach.

    """

    result = []
    var = expand(inputlst[0:1],variables)
    lst = expand(inputlst[1:2],variables)
    for item in lst:
        variables[var[0]] = [item]
        result += expand([inputlst[2]],variables)

    return result

def wildcard(inputlst,variables):
    """GNU makefile wildcard

    """
    command = expand(inputlst,variables)
    return glob.glob(command[0])

def shell(inputlst,variables):
    """GNU makefile shell command

    """
    command = ""
    retlst = []
    for item in expand(inputlst,variables):
        command += item + " "
    (status,returnstr) = getstatusoutput(command)
    if status:
        print("Error with command" + command)
    for item in returnstr.split():
        retlst.append(item)
    return retlst

def notdir(inputlst,variables): #strip the dir from the file name
    """GNU makefile notdir

    """
    if isinstance(inputlst[0],list):
        files = expand(inputlst,variables)
    else:
        files = inputlst[0].split()

    notdirf = []
    for file in files:
        notdirf.append(os.path.split(file)[1])

    return notdirf

funcdict = {
        "foreach" : foreach,
        "wildcard" : wildcard,
        "shell" : shell,
        "notdir" : notdir,
        }

#print(com_interp("(shell pkg-config --cflags libsoup-2.4 $(x))",{"x":["gtk+-2.0"], "y":[".py"], "z":["u"]}))

