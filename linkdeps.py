import os
from subprocess import getstatusoutput

def deptopackage(dep,addpaths):
    print(dep)
    incpaths = ["/usr/include", "/usr/local/include"]
    incpaths += addpaths
    depname = os.path.split(dep)[1]

    (statuscode,packagestr) = getstatusoutput("qfile -C " + depname)
    if not statuscode == 0:
        print("something went wrong...") #have it print a more useful error!
        return

    packagelst = packagestr.split()
    package = []
    n = 0
    for depfile in packagelst[1::2]:
        for incpath in incpaths:
            if depfile.strip("()") == (incpath + "/" + dep):
                package.append(packagelst[n])
        n += 2

    if len(package) > 1:
        print("more than one matching package where found!")

    print(package)
    if not package:
        print("not matching package found withing the include paths!")
        package = ["dummy"]
    return package

