import os
import glob
from ply import lex
from ply import yacc

global_hfiles = set()
local_hfiles = set()

def scandir(dir, filetype):
    files = []
    dirs = [f for f in os.listdir(dir)
        if os.path.isdir(os.path.join(dir, f))]
    for dir_path in dirs:
        files += scandir(dir + "/" + dir_path, filetype)
    return files + glob.glob(dir + "/*" + filetype)

#print(scandir("/home/zed/Desktop/test/smw/", ".cpp"))

#lex stuff begins here

input_string = ""

with open("test.h", encoding="utf-8") as inputfile:
    input_string = inputfile.read()
    print(input_string)

tokens = (
        "INCLUDE",
        "GLOBH",
        "LOCALH",
        "BUNDLEINC"
        )

t_ignore = " \t"

def t_comment(t):
    r'(/\*(.|\n)*\*/)|(//.*)'
    pass

def t_INCLUDE(t):
    r"\#[Ii][Nn][Cc][Ll][Uu][Dd][Ee]"
    return t

def t_GLOBH(t):
    r"<.*\.h>"
    t.value = t.value[1:-1] #strip <>
    return t

def t_LOCALH(t):
    r"\".*\.h\""
    t.value = t.value[1:-1] #strip ""
    return t

def t_BUNDLEINC(t): #for <string> etc.
    r"<.*>"
    return t

def t_error(t):
    #print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()

#lexer.input(input_string)
#
#for tok in lexer:
#    print(tok)
#
#YACC stuff here

def p_includes2(p):
    """
    includes : includes ginc
             | includes linc
    """

def p_includes(p):
    """
    includes : ginc
             | linc
    """

def p_ginclude(p):
    "ginc : INCLUDE GLOBH"
    needed_hfiles.add(p[2])

def p_linclide(p):
    "linc : INCLUDE LOCALH"
    needed_hfiles.add(p[2])

def p_error(p):
    #print("syntax error at '%s'" % p.value)
    pass

yacc.yacc()

print(yacc.parse(input_string))
print(needed_hfiles)
