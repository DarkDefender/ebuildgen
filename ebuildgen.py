from time import strftime
from subprocess import getstatusoutput

eclass = {
        "git" : "git",
        "svn" : "subversion",
        "hg"  : "mercurial",
        }

arch = getstatusoutput("portageq envvar ARCH")[1]

def genebuild(iuse,deps,dltype,adress,targets,binaries):
    installmethod = guessinstall(targets,binaries)
    outstr = outputebuild(iuse,deps,dltype,adress,installmethod)
    f = open("/tmp/workfile.ebuild","w")
    f.write(outstr)
    f.close()

def guessinstall(targets,binaries):
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

def outputebuild(iuse,deps,dltype,adress,installmethod):
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
        iusestr += (flag + " ")
    iusestr += '"\n'

    text.append(iusestr)

    depstr = 'DEPEND="'
    for dep in deps:
        depstr += (dep + "\n\t")

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
