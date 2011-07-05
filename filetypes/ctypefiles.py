import glob
from ply import lex
from ply import yacc

#lex stuff begins here

def scanincludes(string,inclst,curdir):
    """Scan ctype files for #includes

    Adds and returns new includes to the supplied include list
    input:
    string with the file contents to scan,
    a include list
    string with the current working dir
    """
    tokens = (
            "GINCLUDE",
            "LINCLUDE",
            #"BUNDLEINC",
            "IFDEF",
            "ENDIF",
            )

    states = (
            ("com","exclusive"), #comment
            ("ifdef","inclusive"),
            )

    t_ANY_ignore = " \t"

    def t_begin_com(t):
        r"/\*"
        t.lexer.push_state("com")

    def t_com_end(t):
        r"\*/"
        t.lexer.pop_state()
        pass

    def t_line_com(t):
        r"//.*"
        pass

    def t_ANY_begin_if0(t):
        r"\#if[ \t]+0"
        t.lexer.push_state("com")

    def t_com_endif(t):
        r"\#endif"
        t.lexer.pop_state()
        pass

    def t_com_ifdef(t):
        r"\#ifdef"
        t.lexer.push_state("com")

    def t_IFDEF(t):
        r"\#ifdef[ \t]+[a-zA-Z_][a-zA-Z0-9_]*"
        t.value = t.value[6:].strip() #return the ifdef name
        t.lexer.push_state("ifdef")
        return t

    def t_ifdef_ENDIF(t):
        r"\#endif"
        t.lexer.pop_state()
        return t

    def t_GINCLUDE(t):
        r"\#[Ii][Nn][Cc][Ll][Uu][Dd][Ee][ \t]+<.*\.h>"
        t.value = t.value[8:].strip().strip("<>")
        return t

    def t_LINCLUDE(t):
        r"\#[Ii][Nn][Cc][Ll][Uu][Dd][Ee][ \t]+\".*\.h\""
        t.value = t.value[8:].strip().strip('""')
        return t

    def t_BUNDLEINC(t):
        r"\#[Ii][Nn][Cc][Ll][Uu][Dd][Ee][ \t]+<.*>"
        pass

    def t_ANY_error(t):
        #print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    lexer = lex.lex()

    #lexer.input(string)
    #
    #for tok in lexer:
    #    print(tok)
    #
    #YACC stuff here

    def p_includes2(p):
        """
        includes : includes ginc
        """
        p[1][0].add(p[2])
        p[0] = p[1]

    def p_lincludes(p):
        """
        includes : includes linc
        """
        if islocalinc(p[2],curdir):
            p[1][1].add(p[2])
        else:
            p[1][0].add(p[2])
        p[0] = p[1]

    def p_ifdef(p):
        """
        includes : includes IFDEF includes ENDIF
                 | IFDEF includes ENDIF
        """
        if len(p) == 5:
            p[1][2] = addnewifdefs(p[1][2],{p[2] : p[3]})
            p[0] = p[1]
        else:
            ifdef = {}
            ifdef[p[1]] = p[2]
            p[0] = [set(),set(),ifdef]

    def p_ginc(p):
        "includes : ginc"
        globinc = set()
        globinc.add(p[1])
        p[0] = [globinc,set(),{}]

    def p_linc(p):
        "includes : linc"
        locinc = set()
        locinc.add(p[1])
        if islocalinc(p[1], curdir):
            p[0] = [set(),locinc,{}]
        else:
            p[0] = [locinc,set(),{}]

    def p_ginclude(p):
        "ginc : GINCLUDE"
        p[0] = p[1]

    def p_linclude(p):
        "linc : LINCLUDE"
        p[0] = p[1]

    def p_error(p):
        #print("syntax error at '%s'" % p.type)
        pass

    yacc.yacc()

    newinclst = yacc.parse(string)
    if newinclst == None:
        #Check if the file didn't have any includes
        return(inclst)
    newinclst = addnewincludes(newinclst,inclst)
    return(newinclst)

def islocalinc(inc, curdir):
    """Checks if this is a local include

    Checks if the file can be found with the path the is supplied.
    If not this is probably a global include and thus return False
    """

    if glob.glob(curdir + "/" + inc) == []:
        return False
    else:
        return True


def addnewincludes(inclist1,inclist2):
    """Adds new includes to the first inclist and return it

    Does a deeper scan for ifdef includes
    """
    #come up with better names!!
    inclist1[0] = inclist1[0] | inclist2[0]
    inclist1[1] = inclist1[1] | inclist2[1]
    inclist1[2] = addnewifdefs(inclist1[2],inclist2[2])
    return(inclist1)

def addnewifdefs(dict1,dict2):
    """Merges the ifdef section of the inclst

    Returns a new list with all of the ifdefs
    """

    if dict1 == {} and dict2 == {}:
        #we are done here
        return(dict())
    dups = dict1.keys() & dict2.keys()
    if dups == set():
        #no duplicates, empty set()
        for name in dict2:
            dict1[name] = dict2[name]
        return(dict1)

    for name in dups:
        dict1[name][0] = dict1[name][0] | dict2[name][0]
        dict1[name][1] = dict1[name][1] | dict2[name][1]
        dict1[name][2] = addnewifdefs(dict1[name][2],dict2[name][2])
    return(dict1)
