from subprocess import call
import sys

cmdlineget = {
        "svn" : "svn checkout ",
        "git" : "git clone ",
        "hg"  : "hg clone ",
        "www" : "wget ",
        }

def getsourcecode(adress,repotype):
    callstr = cmdlineget[repotype]

    try:
        retcode = call(callstr + adress + " /tmp/ebuildgen/curproj",shell=True)
        if retcode < 0:
            print("Child was terminated by signal", -retcode, file=sys.stderr)
        else:
            print("Child returned", retcode, file=sys.stderr)
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)
