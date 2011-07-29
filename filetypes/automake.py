from ply import lex
from ply import yacc
import glob
import os

def scanamfile(amfile):
    """Scan automake (.am) file

    Returns ...
    """
    amfile = "\n" + amfile #Add \n so you can guess vars
    tokens = (
            "END",
            "COL",
            "EQ",
            "PEQ",
            "CVAR",
            "MVAR",
            "TEXT",
            "ENDTAB",
            "SPACE",
            "IF",
            "ELSE",
            "ENDIF",
            )

    states = (
            ("com", "exclusive"), #comment
            ("var", "inclusive"),
            ("if", "exclusive"),
            )

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

    def t_ifbegin(t):
        #ugly hack to ensure that this is at the begining of the line and keep the newline token.
        #PLY doesn't support the "^" beginning of line regexp :,(
        r"\nif"
        t.type = "END"
        t.lexer.push_state("if")
        return t

    def t_if_IF(t):
        #http://www.gnu.org/s/hello/manual/automake/Usage-of-Conditionals.html#Usage-of-Conditionals
        r"[ \t]+[^ \n\t]*"
        t.value = t.value.strip() #take the variable to test
        t.lexer.pop_state()
        return t

    def t_ELSE(t):
        r"\nelse"
        return t

    def t_ENDIF(t):
        r"\nendif"
        return t

    def t_CVAR(t): #configure variable
        r"@.*?@" #not greedy
        return t

    def t_MVAR(t): #makefile variable
        r"\$\(.*?\)"
        return t

    def t_com_END(t):
        r"\n"
        t.lexer.begin("INITIAL")
        t.lexer.lineno += 1
        return t

    def t_EQ(t):
        r"[ \t]*=[ \t]*"
        t.lexer.begin("var")
        t.value = t.value.strip()
        return t

    def t_PEQ(t):
        r"[ \t]*\+=[ \t]*"
        t.lexer.begin("var")
        t.value = t.value.strip()
        return t

    def t_contline(t):
        r"\\\n"
        t.lexer.lineno += 1
        pass

    def t_litteral(t):
        r"\\."
        t.value = t.value[1] #take the literal char
        t.type = "TEXT"
        return t

    def t_COL(t):
        r"[ \t]*:[ \t]*"
        t.lexer.begin("var")
        return t

    def t_var_ENDTAB(t):
        r"[ \t]*;[ \t]*"
        return t

    def t_ENDTAB(t):
        r"[ \t]*\n\t[ \t]*"
        t.lexer.lineno += 1
        return t

    def t_var_TEXT(t):
        r"[^ #\n\t,\$@\\]+"
        return t

    def t_TEXT(t):
        r"[^ \n\t:=\$@\\]+"
        return t

    def t_END(t):
        r"[ \t]*\n"
        t.lexer.lineno += t.value.count('\n')
        t.lexer.begin('INITIAL')
        return t

    def t_var_SPACE(t):
        r"[ \t]+"
        return t

    def t_space(t):
        r"[ \t]"
        pass

    def t_var_special(t):
        r"\$[^({]"
        t.type = "TEXT"
        return t

    def t_ANY_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    lexer = lex.lex()

    #lexer.input(amfile)
    #for tok in lexer:
    #    print(tok)

    #YACC stuff begins here

    def p_done(p):
        "done : vars end"
        p[0] = p[1]

    def p_vars(p):
        """
        vars : vars end var
             | end var
        """
        if len(p) == 4:
            p[1][0].update(p[3][0])
            p[1][2].update(p[3][2])
            p[0] = [p[1][0], p[1][1] + p[3][1], p[1][2]]

        else:
            p[0] = p[2]

    def p_if(p):
        """
        var : IF vars ENDIF
            | IF vars ELSE vars ENDIF
        """
        if len(p) == 4:
            p[0] = [{},[],{p[1]:p[2]}]

        else:
            p[0] = [{},[],{p[1]:p[2],"!"+p[1]:p[4]}]

    def p_var(p):
        """
        var : textstr EQ textlst
            | textstr EQ
            | textstr PEQ textlst
        """
        if p[2] == "=":
            if len(p) == 4:
                p[0] = [{p[1]: p[3]},[],{}]
            else:
                p[0] = [{p[1]: []},[],{}]
        else:
            p[0] = [{},[[p[1], p[3]]],{}]

    def p_textlst(p):
        """
        textlst : textlst spacestr textstr
                | textstr
        """
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    def p_teststr(p):
        """
        textstr : textstr TEXT
                | textstr CVAR
                | textstr MVAR
                | TEXT
                | CVAR
                | MVAR
        """
        if len(p) == 3:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1]

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
            | END
        """

    def p_error(p):
        print("syntax error at '%s'" % p.type,p.value)
        pass

    yacc.yacc()

    variables = yacc.parse(amfile)
    return variables

def initscan(amfile,iflst):
    useflag_sources = {}  #{source: [useflag, value]}

    def scan(amfile):
        curdir = os.path.split(amfile)[0] + "/"
        amlist = scanamfile(openfile(amfile))
        #print(amfile)

        def sources_to_scan(amlist,curdir):
            sources = []
            extra_sources = []
            #perhaps use set() here to eliminate the possibilty of duplicates?
            for variable in amlist[0]:
                if variable.split("_")[-1] == "SOURCES":
                    if variable.split("_")[0] == "EXTRA":
                        extra_sources += amlist[0][variable]
                    else:
                        sources += amlist[0][variable]

                if variable.split("_")[-1] == "LDADD":
                    for item in amlist[0][variable]:
                        if item[0] == "@" and item[-1] == "@":
                            for ifstate in iflst:
                                if item.strip("@") in ifstate[1]:
                                    for file in ifstate[1][item.strip("@")]:
                                        for src in extra_sources:
                                            if file.split(".")[0] == src.split(".")[0]:
                                                useflag_sources.update({curdir + src : ifstate[0]})

                        for src in extra_sources:
                            if item.split(".")[0] == src.split(".")[0]:
                                sources += [src]

            if "SUBDIRS" in amlist[0]:
                for dir in amlist[0]["SUBDIRS"]:
                    sources += scan(curdir + dir + "/Makefile.am")

            for lst in amlist[1]:
                if lst[0] == "SUBDIRS":
                    for dir in lst[1]:
                        sources += scan(curdir + dir + "/Makefile.am")

            for ifstatement in amlist[2]:
                #print(ifstatement)
                for item in iflst:
                    if ifstatement.lstrip("!") in item[1]:
                        if ifstatement[0] == "!":
                            if item[1][ifstatement.lstrip("!")] == "false":
                                for src in sources_to_scan(amlist[2][ifstatement],curdir):
                                    useflag_sources.update({src : item[0]})

                        elif item[1][ifstatement] == "true":
                            for src in sources_to_scan(amlist[2][ifstatement],curdir):
                                useflag_sources.update({src : item[0]})

            #add filepath
            dirsources = []
            for source in sources:
                if os.path.split(source)[0] == "":
                    dirsources += [curdir + source]
                else:
                    dirsources += [source]

            return dirsources

        return sources_to_scan(amlist,curdir)
    return scan(amfile),useflag_sources

def openfile(ofile):
    with open(ofile, encoding="utf-8", errors="replace") as inputfile:
        return inputfile.read()
