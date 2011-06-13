#!/usr/bin/python3

import argparse
import scanfiles
import linkdeps
import ebuildgen

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

args = parser.parse_args()

#print(args.dir)
#print(args.types)

#inclst is a list of includes. First in it is global then local.

(inclst,binaries,targets) = scanfiles.scanproject(args.dir,"makefile")
packages = set()
print(binaries)
for dep in inclst[0]:
    packages.add(linkdeps.deptopackage(dep)[0])

ebuildgen.genebuild([],packages,"svn","http://doneyet.googlecode.com/svn/trunk",targets,binaries)

if args.ginc == args.linc == args.ifdef == args.quiet == False:
    print(inclst)
    print(packages)

if args.ginc:
    print(inclst[0])
if args.linc:
    print(inclst[1])

if args.ifdef:
    for name in inclst[2]:
        print(name)
        print(inclst[2][name][0])
        print(inclst[2][name][1])
