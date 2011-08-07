#!/usr/bin/python3

import argparse
import scanfiles
import linkdeps
import ebuildgen
from scmprojects import getsourcecode

parser = argparse.ArgumentParser(
        description="Scan a dir for files and output includes",
        epilog="Example: cli.py ~/my/project -t .c .h")

parser.add_argument("dir")
parser.add_argument("-t", "--types", metavar="filetype", nargs="+",
                    default=[".c",".cpp",".h"],
                    help="what filetypes it should scan")
parser.add_argument("-g", "--ginc", action="store_true",
                    help="print global includes")
parser.add_argument("-l", "--linc", action="store_true",
                    help="print local includes")
parser.add_argument("-d", "--ifdef", action="store_true",
                    help="print includes the depends on ifdefs")
parser.add_argument("-q", "--quiet", action="store_true",
                    help="don't print anything")  #this needs work...

parser.add_argument("--svn", action="store_true",
                    help="this is a SVN project")
parser.add_argument("--git", action="store_true",
                    help="this is a GIT project")
parser.add_argument("--hg", action="store_true",
                    help="this is a HG project")

args = parser.parse_args()

#print(args.dir)
#print(args.types)

#inclst is a list of includes. First in it is global then local.
if args.svn:
    getsourcecode(args.dir,"svn")
    srcdir = "/tmp/ebuildgen/curproj"
    dltype = "svn"
elif args.git:
    getsourcecode(args.dir,"git")
    srcdir = "/tmp/ebuildgen/curproj"
    dltype = "git"
elif args.hg:
    getsourcecode(args.dir,"hg")
    srcdir = "/tmp/ebuildgen/curproj"
    dltype = "hg"
else:
    srcdir = args.dir
    dltype = "www"

(iuse,inclst,useargs) = scanfiles.scanproject(srcdir,"autotools")
targets = [["install"]]
binaries = []
gpackages = set()
for dep in inclst[0]:
    gpackages.add(linkdeps.deptopackage(dep,[])[0])
#print(gpackages)
if "__cplusplus" in inclst[2]:
    for dep in inclst[2]["__cplusplus"][0]:
        gpackages.add(linkdeps.deptopackage(dep,[])[0])

usedeps = {}
for use in useargs:
    packages = set()
    for dep in useargs[use][0]:
        newpack = linkdeps.deptopackage(dep,[])[0]
        if not newpack in gpackages:
            packages.add(newpack)
    if "__cplusplus" in useargs[use][2]:
        for dep in useargs[use][2]["__cplusplus"][0]:
            newpack = linkdeps.deptopackage(dep,[])[0]
            if not newpack in gpackages:
                packages.add(newpack)
    usedeps[use] = packages

#print(usedeps)
#print(iuse)
ebuildgen.genebuild(iuse,gpackages,usedeps,dltype,args.dir,targets,binaries)

if args.ginc == args.linc == args.ifdef == args.quiet == False:
    print(inclst)
    print(gpackages)

if args.ginc:
    print(inclst[0])
if args.linc:
    print(inclst[1])

if args.ifdef:
    for name in inclst[2]:
        print(name)
        print(inclst[2][name][0])
        print(inclst[2][name][1])
