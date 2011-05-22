import argparse
import scanfiles

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

args = parser.parse_args()

#print(args.dir)
#print(args.types)

(globinc,localinc) = scanfiles.startscan(args.dir,args.types)

if args.ginc:
    print(globinc)
if args.linc:
    print(localinc)
