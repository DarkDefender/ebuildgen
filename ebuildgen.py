from time import strftime
from subprocess import getstatusoutput

eclass = {
        "git" : "git",
        "svn" : "subversion",
        "hg"  : "mercurial",
        }

arch = getstatusoutput("portageq envvar ARCH")[1]

def genebuild(iuse,deps,usedeps,dltype,adress,targets,binaries):
    """This function starts the ebuild generation.

    You have to provide the following args in order:
    iuse, a list of useflags
    deps, a list of dependecies
    dltype, how to download the source code (wget,GIT,etc)
    adress, Adress to the source code
    targets, a list of build targets for the project (used to guess install method)
    binaries, a list of binaries that is created during compile (used to install them if there is no 'make install')
    """

    installmethod = guessinstall(targets,binaries)
    outstr = outputebuild(iuse,deps,usedeps,dltype,adress,installmethod)
    f = open("/tmp/workfile.ebuild","w")
    f.write(outstr)
    f.close()

def guessinstall(targets,binaries):
    """Guess the install method of the project

    Looks at the make targets for a 'make install'
    if that fails just install the binaries
    """

    targetlst = []
    returnlst = []
    for target in targets:
        targetlst.append(target[0])

    if "install" in targetlst:
        returnlst = ['	emake DESTDIR="${D}" install || die "emake install failed"']
    else:
        for binary in binaries:
            returnlst += ['	dobin ' + binary + ' || die "bin install failed"']

    return returnlst

def outputebuild(iuse,deps,usedeps,dltype,adress,installmethod):
    """Used to generate the text for the ebuild to output

    Generates text with the help of the supplied variables
    """

    text = [
            '# Copyright 1999-' + strftime("%Y") + ' Gentoo Foundation',
            '# Distributed under the terms of the GNU General Public License v2',
            '# $Header: $',
            ''
            ]
    inheritstr = 'inherit ' + eclass[dltype]
    text.append(inheritstr)

    text += [
            '',
            'EAPI=3',
            '',
            'DESCRIPTION=""',
            'HOMEPAGE=""'
            ]
    if dltype == "www":
        srcstr = 'SRC_URI="' + adress + '"'
    else:
        srcstr = 'E' + dltype.upper() + '_REPO_URI="' + adress + '"'
    text.append(srcstr)

    text += [
            '',
            'LICENSE=""',
            'SLOT="0"',
            'KEYWORDS="~' + arch + '"'
            ]
    iusestr = 'IUSE="'
    for flag in iuse:
        iusestr += (flag.split("_")[1] + " ")
    iusestr += '"\n'

    text.append(iusestr)

    depstr = 'DEPEND="'
    for dep in deps:
        depstr += (dep + "\n\t")

    for use in usedeps:
        #check if packagelist is empty
        if usedeps[use]:
            if use[0] == "!":
                depstr += "!" + use.split("_")[1] + "? ( "
            else:
                depstr += use.split("_")[1] + "? ( "

            for dep in usedeps[use]:
                depstr += dep +"\n\t\t"
            depstr = depstr[:-3]
            depstr += " )\n\t"

    depstr = depstr[:-2] + '"'
    text.append(depstr)

    text += [
            'RDEPEND="${DEPEND}"',
            '',
            'src_compile() {',
            '	emake || die "emake failed"',
            '}'
            ]

    text += [
            '',
            'src_install() {',
            ]
    text += installmethod

    text += ['}']

    outputstr = ""
    for line in text:
        outputstr += line + "\n"

    return outputstr
