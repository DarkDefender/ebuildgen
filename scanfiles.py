import os
import glob
from ply import lex
from ply import yacc

needed_hfiles = {}

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
        "LOCALH"
        )

t_ignore = " \t"

def t_comment(t):
    r'(/\*(.|\n)*\*/)|(//.*)'
    pass

def t_INCLUDE(t):
    r"\#[Ii][Nn][Cc][Ll][Uu][Dd][Ee]"
    return t

def t_GLOBH(t):
    r"<.*>"
    return t

def t_LOCALH(t):
    r"\".*\""
    return t

def t_error(t):
    #print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()

lexer.input(input_string)

for tok in lexer:
    print(tok)
