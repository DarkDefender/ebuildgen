from subprocess import call
import sys
import glob
import shutil

cmdlineget = {
        "svn" : "svn checkout ",
        "git" : "git clone ",
        "hg"  : "hg clone ",
        "www" : "wget ",
        }

def getsourcecode(adress,repotype):
    """This downloads the sourcecode to /tmp/ebuildgen/curproj

    Supply the adress to the source code and repo type
    """
    callstr = cmdlineget[repotype]

    if glob.glob("/tmp/ebuildgen/curproj"):
        #this is might not be the best solution
        shutil.rmtree("/tmp/ebuildgen/curproj")

    try:
        retcode = call(callstr + adress + " /tmp/ebuildgen/curproj",shell=True)
        if retcode < 0:
            print("Child was terminated by signal", -retcode, file=sys.stderr)
        else:
            print("Child returned", retcode, file=sys.stderr)
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)
