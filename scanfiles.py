import os
import glob
from filetypes.ctypefiles import scanincludes
from filetypes.makefiles import scanmakefile
from filetypes.makefilecom import expand

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
    olddir = os.getcwd()
    makefile = openfile(makefile)
    binaries = set() #the binaries that the .o file create
    filestoscan = set()
    impfiles = [] #look for these files
    moptions = [] #make options scan these for -I... flags
    os.chdir(curdir) #so makefiles commands can execute in the correct dir
    targets,variables = scanmakefile(makefile)
    deps = targets[0][1] #Use first make target
    while deps != []:
        newdeps = []
        for dep in deps:
            for target in targets:
                if target[0] == dep:
                    newdeps += target[1]
                    if ".o" in dep or dep in impfiles:
                        impfiles += target[1]
                        moptions += target[2]
                    elif ".o" in target[1][0]:
                        binaries.add(target[0])
                        moptions += target[2]
        deps = newdeps

    #print(impfiles)
    for impfile in impfiles:
        filestoscan.add(curdir + impfile)

    incflags = set()
    for item in expand(moptions,variables):
        if item[0:2] == "-I":
            incflags.add(item[2:])

    #print(filestoscan)
    os.chdir(olddir)
    return filestoscan,binaries,incflags,targets

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
        filestolookfor = ["Makefile","makefile"]

    mfile = scandirfor(dir, filestolookfor)[0] #use first file found
    print(mfile)
    (scanlist,binaries,incflags,targets) = scanmakefiledeps(mfile)
    return scanfilelist(scanlist),binaries,incflags,targets

def openfile(file):
    try:
        with open(file, encoding="utf-8", errors="replace") as inputfile:
            return inputfile.read()
    except IOError:
        print('cannot open', file)
