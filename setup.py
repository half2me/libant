#!/usr/bin/env python

from distutils.core import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='LibAnt',
      version='0.1.2',
      description='Python Ant+ Lib',
      author='Benjamin Tamasi',
      author_email='h@lfto.me',
      url='https://github.com/half2me/libAnt',
      install_requires=requirements,
      licence='MIT',
      packages=['libAnt', 'libAnt.profiles'],
      )
