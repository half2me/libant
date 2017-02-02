#!/usr/bin/env python3

from setuptools import setup

setup(
    name='LibAnt',
    packages=['libAnt', 'libAnt.profiles', 'libAnt.drivers', 'libAnt.loggers'],
    version='0.1.7',
    description='Python Ant+ Lib',
    author='glevente',
    author_email='levente.gergely@ccsys.eu',
    url='https://github.com/half2me/libAnt',
    download_url='https://github.com/half2me/libAnt/tarball/0.1.3',
    keywords = ['ant', 'antplus', 'ant+', 'antfs', 'thisisant'],
    install_requires=['pyusb>=1.0.0', 'pyserial>=3.1.1'],
)
