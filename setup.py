#!/usr/bin/python

from distutils.core import setup


setup(name='Ebuild generator',
      version='0.1',
      description='Script to generate ebuilds',
      author='Sebasitan Parborg',
      author_email='darkdefende@gmail.com',
      url='https://github.com/DarkDefender/ebuildgen',
      packages=['ebuildgen', 'ebuildgen.filetypes'],
      scripts=['genebuild'],
     )
