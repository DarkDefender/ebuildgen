import os
import glob
from filetypes.ctypefiles import scanincludes
from filetypes.makefiles import scanmakefile

def scandirfor(dir, filetypes):
    files = []
    dirs = [f for f in os.listdir(dir)
        if os.path.isdir(os.path.join(dir, f))]
    for dir_path in dirs:
        files += scandir(dir + "/" + dir_path, filetypes)
    for filetype in filetypes:
        files += glob.glob(dir + "/*" + filetype)
    return files

def scanmakefiledeps(makefile):
    filestoscan = []
    impfiles = [] #look for these files
    targets = scanmakefile(makefile)
    deps = targets[0][1] #Use first make target
    while deps != []:
        newdeps = []
        for dep in deps:
            for target in targets:
                if target[0] == dep:
                    newdeps += target[1]
                    if ".o" in dep or dep in impfiles:
                        impfiles += target[1]
        deps = newdeps

    #impfiles.sort()
    #print(impfiles)
    return impfiles

def scanfilelist(filelist):
    global_hfiles = set()
    local_hfiles = set()
    inclst = [global_hfiles,local_hfiles,{}]

    for file in filelist:
        with open(file, encoding="utf-8", errors="replace") as inputfile:
            inclst = scanincludes(inputfile.read(),inclst,os.path.split(file)[0])

    return(inclst)

fle = "/usr/portage/distfiles/svn-src/doneyet-read-only/trunk/Makefile"
with open(fle, encoding="utf-8", errors="replace") as inputfile:
    scanmakefiledeps(inputfile.read())
