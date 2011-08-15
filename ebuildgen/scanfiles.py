import os
import glob
from ebuildgen.filetypes.ctypefiles import scanincludes
from ebuildgen.filetypes.makefiles import scanmakefile
from ebuildgen.filetypes.makefilecom import expand
from ebuildgen.filetypes.autoconf import scanac
from ebuildgen.filetypes.automake import initscan

def scandirfor(dir, filetypes):
    """Scans recursivly the supplied dir for provided filetypes.

    And return a list of files found
    """

    files = []
    dirs = [f for f in os.listdir(dir)
        if os.path.isdir(os.path.join(dir, f))]
    for filetype in filetypes:
        files += glob.glob(dir + "/*" + filetype)
    for dir_path in dirs:
        files += scandirfor(dir + "/" + dir_path, filetypes)
    return files

def scanmakefiledeps(makefile):
    """Scans makefile for what files it would compile.

    returns a list of files to scan for deps,
    binaries build with the first makefile option,
    additional includeflags and what the 'targets : deps'
    are in the makefile
    """

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

def scanautotoolsdeps(acfile,amfile):
    """Scans autoconf file for useflags and the automake file in the same dir.

    Scans the provided autoconf file and then looks for a automakefile in the
    same dir. Autoconf scan returns a dict with useflags and a list with variables
    that gets defined by those useflags.

    Call the automake scan with the am file (that is in the same dir as the ac file)
    and the list of variables from the autoconf scan and it will return a list of
    default source files and a dict of files that gets pulled in by the useflag it
    returns.
    """
    #these are not really useflags yet. So perhaps change name?
    topdir = os.path.split(amfile)[0] + "/"
    useflags, iflst = scanac(openfile(acfile),topdir)
    srcfiles, src_useflag, src_incflag = initscan(amfile, iflst)

    #print(iflst)
    #print(srcfiles)
    #print(src_useflag)
    #standard includes
    includes = scanfilelist(srcfiles,src_incflag)

    def inter_useflag(uselst):
        if uselst[1] == "yes" or uselst[1] == "!no":
            usearg = uselst[0]
        elif uselst[1] == "no" or uselst[1] == "!yes":
            usearg = "!" + uselst[1]
        else:
            usearg = uselst[0] + "=" + uselst[1]

        return usearg

    #useflag includes
    useargs = {}
    for src in src_useflag:
        usearg = inter_useflag(src_useflag[src])
        if usearg in useargs:
            useargs[usearg] += [src]
        else:
            useargs[usearg] = [src]

    ifdef_lst = [includes[2]]

    for usearg in useargs:
        useargs[usearg] = scanfilelist(useargs[usearg],src_incflag)
        ifdef_lst += [useargs[usearg][2]]

    for ifdef in ifdef_lst:
        for item in ifdef:
            for switch in iflst:
                if item in switch[1]:
                    usearg = inter_useflag(switch[0])
                    if usearg in useargs:
                        useargs[usearg][0].update(ifdef[item][0])
                    else:
                        useargs[usearg] = ifdef[item]
    #print(useargs)
    #print(includes)
    return useflags,includes,useargs

def scanfilelist(filelist,src_incflag):
    """ Scan files in filelist for #includes

    returns a includes list with this structure:
    [set(),set(),dict()]
    There the first two sets contains global and local includes
    and the dict contains variables that can pull in additional includes
    with the same structure as above
    """
    global_hfiles = set()
    local_hfiles = set()
    inclst = [global_hfiles,local_hfiles,{}]

    for file in filelist:
        #print(file)
        incpaths = src_incflag[file]
        filestring = openfile(file)
        if not filestring == None:
            inclst = scanincludes(filestring,inclst,os.path.split(file)[0],incpaths)

    return(inclst)

def scanproject(dir,projecttype):
    """Scan a project (source) dir for files that may build it

    This tries to guess which kind of project it is. IE
    autotools? makefile?
    """
    if projecttype == "guess":
        filestolookfor = ["Makefile","makefile",
    "configure.ac","configure.in"] #add more later
    elif projecttype == "makefile":
        filestolookfor = ["Makefile","makefile"]
    elif projecttype == "autotools":
        filestolookfor = ["configure.ac","configure.in"]

    mfile = scandirfor(dir, filestolookfor)[0] #use first file found
    print(mfile)
    if mfile == "Makefile" or mfile == "makefile":
        (scanlist,binaries,incflags,targets) = scanmakefiledeps(mfile)
    #this is broken now... rewrite
        return scanfilelist(scanlist),binaries,incflags,targets

    else:
        amfile = os.path.split(mfile)[0] + "/" + "Makefile.am"
        return scanautotoolsdeps(mfile,amfile)

def openfile(file):
    """Open a file and return the content as a string.

    Returns nothing and print an error if the file cannot be read
    """
    try:
        with open(file, encoding="utf-8", errors="replace") as inputfile:
            return inputfile.read()
    except IOError:
        print('cannot open', file)
