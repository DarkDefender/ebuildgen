from ply import lex
from ply import yacc

def scanacfile(acfile):
    """Scan a autoconfigure (.in/.ac) file.

    Returns ....
    """

    tokens = (
            "FUNC",
            "COMPFUNC", #complete func
            "FUNCOPT", #func options
            "FUNCEND",
            "VAR",
            "ECHO",
            "TEXT",
            "IF",
            "IFCOM",
            "ELIF",
            "ELSE",
            "THEN",
            "IFEND",
            "CASE",
            "CASEOPT",
            "COPTEND", #case opt end, doesn't need to be there but SHOULD
            "CASEEND",
            "COMMA",
            )

    states = (
            ("func", "inclusive"),
            ("funcopt", "exclusive"),
            ("case", "inclusive"),
            ("if", "inclusive"),
            ("shellcom", "exclusive"),
            )

    def t_contline(t):
        r"\\\n"
        t.lexer.lineno += 1
        pass

    def t_ANY_space(t):
        r"[ \t]"
        pass

    def t_newline(t):
        r"\n"
        t.lexer.lineno += 1
        pass

    def t_shfunc(t): #shell func
        r'[a-zA-Z_][a-zA-Z0-9_]*\(\)[ \t]*{'
        t.lexer.level = 1
        t.lexer.push_state("shellcom")

    def t_shellcom_text(t):
        r"[^{}]+"

    def t_shellcom_opb(t):
        r"{"
        t.lexer.level +=1

    def t_shellcom_opc(t):
        r"}"
        t.lexer.level -=1

        if t.lexer.level == 0:
            t.lexer.pop_state()
            pass

    def t_COMPFUNC(t):
        r'[a-zA-Z_][a-zA-Z0-9_]*\([^\\[\](\),]*\)'
        values = t.value.split("(")
        t.value = [values[0],values[1][:-1]]
        return t

    def t_FUNC(t):
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

    def t_funcopt_contline(t):
        r"\\\n"

    def t_func_COMMA(t):
        r","
        return t

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
        #take var=text, var="text text", var='text text', var=`text text`
        r"[a-zA-Z_][a-zA-Z0-9_]*=(\"[^\"]*\"|\'[^\']*\'|\`[^\`]*\`|[^() \t,\n]*)+"
        t.lexer.lineno += t.value.count('\n')
        return t

    def t_IF(t):
        r"if"
        t.lexer.push_state("if")
        return t

    def t_ELIF(t):
        r"elif"
        t.lexer.push_state("if")
        return t

    def t_if_THEN(t):
        r"then"
        t.lexer.pop_state()
        return t

    def t_if_IFCOM(t):
        r"[^ \t\n]+"
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
        r"[^\n\t\(\)]+\)"
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
        #Fix this so I can handle variables like the one above as that is NOT a text string
        r"([^ ;,\t\n\(\)]+|\([^() \t\n]*\))"
        return t

    def t_ANY_error(t):
        print("Illegal character '%s'" % t.value[0],t.lexer.lineno)
        t.lexer.skip(1)

    lexer = lex.lex()

    #lexer.input(acfile)
    #for tok in lexer:
    #    print(tok)

    #YACC stuff begins here

    def p_complst(p):
        """
        complst : complst text
                | complst ECHO
                | complst func
                | complst VAR
                | complst ifcomp
                | complst case
                | complst FUNCOPT
                | text
                | ECHO
                | func
                | VAR
                | ifcomp
                | case
                | FUNCOPT
        """
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    def p_text(p):
        """
        text : text TEXT
             | TEXT
        """
        if len(p) == 3:
            p[0] = p[1] + " " + p[2]
        else:
            p[0] = p[1]

    def p_case(p):
        """
        case : CASE caseopt CASEEND
        """
        p[0] = [p[1]] + [p[2]]

    def p_caseopt(p):
        """
        caseopt : caseopt CASEOPT complst COPTEND
                | CASEOPT complst COPTEND
        """
        if len(p) == 5:
            p[0] = p[1] + [p[2], p[3]]
        else:
            p[0] = [p[1], p[2]]

    def p_caseopt2(p):
        """
        caseopt : caseopt CASEOPT complst
                | caseopt CASEOPT COPTEND
                | CASEOPT complst
                | CASEOPT COPTEND
        """
        if len(p) == 4:
            if isinstance(p[3],list):
                p[0] = p[1] + [p[2], p[3]]
            else:
                p[0] = p[1] + [p[2], []]
        else:
            if isinstance(p[2],list):
                p[0] = [p[1], p[2]]
            else:
                p[0] = [p[1], []]

    def p_ifcomp(p): #perhaps needs elif also
        """
        ifcomp : if IFEND
        """
        p[0] = p[1]

    def p_if(p):
        """
        if : if ELSE complst
           | IF ifcom THEN complst
           | if ELIF ifcom THEN complst
        """
        if len(p) == 5:
            p[0] = [[p[1]] + [p[2]], p[4]]

        elif len(p) == 6:
            p[0] = p[1] + [[p[2]] + [p[3]], p[5]]

        else:
            p[0] = p[1] + [[p[2]], p[3]]


    def p_ifcom(p):
        """
        ifcom : ifcom IFCOM
              | IFCOM
        """
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    def p_func(p):
        """
        func : FUNC funcopt FUNCEND
             | COMPFUNC
        """
        if len(p) == 2:
            p[0] = p[1] #this is already ordered
        else:
            p[0] = [p[1],p[2]]

    def p_funccomma(p):
        """
        funcopt : funcopt COMMA
                | COMMA complst
                | COMMA
        """
        if len(p) == 3:
            if isinstance(p[2],list):
                if len(p[2]) > 1:
                    p[0] = [[]] + [p[2]]
                else:
                    p[0] = [[]] + p[2]

            else:
                p[0] = p[1] + [[]]
        else:
            p[0] = [[]]

    def p_funcopt(p):
        """
        funcopt : funcopt COMMA complst
                | complst
        """
        if len(p) == 4:
            if len(p[3]) > 1:
                p[0] = p[1] + [p[3]]
            else:
                p[0] = p[1] + p[3]
        else:
            if len(p[1]) > 1:
                p[0] = [p[1]]
            else:
                p[0] = p[1]

    def p_error(p):
        print("syntax error at '%s'" % p.type,p.value)
        pass

    yacc.yacc()

    items = yacc.parse(acfile)
    return items

from acif import parseif

def output(inputlst):
    variables = dict()
    ifs = []
    for item in inputlst:
        if item[0] == "AC_ARG_ENABLE":
            name = convnames(item[1][0])
            if len(item[1]) == 2:
                variables["enable_" + name] = [[],[]]
            elif len(item[1]) == 3:
                variables["enable_" + name] = [item[1][2],[]]
            else:
                variables["enable_" + name] = [item[1][2],item[1][3]]

        #remember to convert chars in the name of "item[1]" that is not
        #alfanumeric char to underscores _

        if item[0] == "AC_ARG_WITH":
            name = convnames(item[1][0])
            if len(item[1]) == 2:
                variables["with_" + name] = [[],[]]
            elif len(item[1]) == 3:
                variables["with_" + name] = [item[1][2],[]]
            else:
                variables["with_" + name] = [item[1][2],item[1][3]]
        elif isinstance(item[0],list): #if statements
            for variable in variables:
                for pattern in item[0][1]:
                    if variable in pattern:
                        ifs += [parseif(item[0][1])]
        elif "=" in item:
            #print(item)
            b = 0

    #for variable in variables:
        #print(variable)
        #print(variables[variable])
    print(ifs)

import re
def convnames(string): #strip none alfanumeric chars and replace them with "_"
    string = string.strip("[]") #remove quotes
    pattern = re.compile("\W")
    newstr = re.sub(pattern, "_", string)
    return newstr

file="configure.in"

with open(file, encoding="utf-8", errors="replace") as inputfile:
    output(scanacfile(inputfile.read()))
