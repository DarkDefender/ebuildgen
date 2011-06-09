import os
import glob
from filetypes.ctypefiles import scanincludes
from filetypes.makefiles import scanmakefile

def scandirfor(dir, filetypes):
    files = []
    dirs = [f for f in os.listdir(dir)
        if os.path.isdir(os.path.join(dir, f))]
    for filetype in filetypes:
        files += glob.glob(dir + "/*" + filetype)
    for dir_path in dirs:
        files += scandirfor(dir + "/" + dir_path, filetypes)
    return files

def scanmakefiledeps(makefile):
    curdir = os.path.split(makefile)[0] + "/"
    makefile = openfile(makefile)
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
    for impfile in impfiles:
        filestoscan.append(curdir + impfile)
    #print(filestoscan)
    return filestoscan

def scanfilelist(filelist):
    global_hfiles = set()
    local_hfiles = set()
    inclst = [global_hfiles,local_hfiles,{}]

    for file in filelist:
        filestring = openfile(file)
        if not filestring == None:
            inclst = scanincludes(filestring,inclst,os.path.split(file)[0])

    return(inclst)

def scanproject(dir,projecttype):
    if projecttype == "guess":
        filestolookfor = ["Makefile","makefile"] #add more later
    elif projecttype == "makefile":
        filestolookfor = ["Makefile","makeifle"]

    mfile = scandirfor(dir, filestolookfor)[0] #use first file found
    print(mfile)
    return scanfilelist(scanmakefiledeps(mfile))

def openfile(file):
    try:
        with open(file, encoding="utf-8", errors="replace") as inputfile:
            return inputfile.read()
    except IOError:
        print('cannot open', file)
