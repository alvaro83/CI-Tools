#!/usr/bin/env python
import os
from setuptools import setup, find_packages

__name__ = 'CI Tools'
__version__ = '1.0.0'

libs_location= os.path.dirname(os.path.abspath(__file__))
os.chdir(libs_location)

print
print "## Install CI Tools python libraries"
setup(name=__name__,
      version=__version__,
      description='Python Distribution CI Tools',
      author='Alvaro Gonzalez Arroyo',
      author_email='alvaro.g.arroyo@gmail.com',
      packages=(find_packages())
      )
