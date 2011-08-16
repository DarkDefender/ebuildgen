# Copyright 1999-2011 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI=3

PYTHON_DEPEND="3:3.2"
SUPPORT_PYTHON_ABIS=1
RESTRICT_PYTHON_ABIS="2.*"
inherit git distutils

DESCRIPTION="A python script to generate ebuilds for autotool C/C++ projects"
HOMEPAGE=""
EGIT_REPO_URI="git://github.com/DarkDefender/ebuildgen.git"

LICENSE=""
SLOT="0"
KEYWORDS=""
IUSE=""

DEPEND="dev-python/ply
	app-portage/gentoopm
	app-portage/portage-utils"
RDEPEND="${DEPEND}"

src_prepare() {
	distutils_src_prepare
}

src_compile() {
	distutils_src_compile
}

src_install() {
	distutils_src_install
}
