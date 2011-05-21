import argparse
import scanfiles

parser = argparse.ArgumentParser(
        description="Scan a dir for files",
        epilog="Example: cli.py ~/my/project -t .c .h")

parser.add_argument("dir")
parser.add_argument("-t", "--types", metavar="filetype", nargs="+",
                    help="what filetypes it should scan")

args = parser.parse_args()

#print(args.dir)
#print(args.types)

print(scanfiles.startscan(args.dir,args.types))
