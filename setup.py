#!/usr/bin/env python3

from distutils.core import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='LibAnt',
    packages=['libAnt', 'libAnt.profiles'],
    version='0.1.2',
    description='Python Ant+ Lib',
    author='Benjamin Tamasi',
    author_email='h@lfto.me',
    url='https://github.com/half2me/libAnt',
    download_url='https://github.com/half2me/libAnt/tarball/0.1.2',
    keywords = ['ant', 'antplus', 'ant+', 'antfs', 'thisisant'],
    install_requires=requirements,
)
