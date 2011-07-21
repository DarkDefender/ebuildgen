import os
from subprocess import getstatusoutput
from urllib.request import urlopen

def deptopackage(dep,addpaths):
    """Converts supplied deps with additional include paths to portage packages

    This uses qfile to quess which package certain files belongs to.
    """

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
        print("not matching package found within the include paths!")
        package = ["dummy"]
    return package

def pfltopackage(dep,addpaths):
    """This uses the online ply database to guess packages

    """

    incpaths = ["/usr/include", "/usr/local/include"]
    incpaths += addpaths

    url_lines = []
    depname = os.path.split(dep)[1]
    matching_packages = set()

    url = urlopen("http://www.portagefilelist.de/index.php/Special:PFLQuery2?file="
            + depname + "&searchfile=lookup&lookup=file&txt")

    for line in url:
        url_lines += [line.decode("utf-8").split()]

    #First line does not contain any useful information, skip it
    url_lines = url_lines[1:]
    #structure of lines: [portage_category, package, path, file, misc, version]

    for line in url_lines:
        #check if path is correct
        for path in incpaths:
            if line[2] + line[3] == path + dep:
                matching_packages.add(line[0] + "/" + line[1])

    if len(matching_packages) > 1:
        print("More than one matching package for dep found!\nPicking the last one...")

    if not matching_packages:
        print("not matching package found within the include paths!")
        print("file not found was:" + dep)
        print("a dummy dep will be placed in the ebuild, fix it!")
        package = ["dummy"]

    print([matching_packages.pop()])

#pfltopackage("ncurses.h",[])
