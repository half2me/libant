#!/usr/bin/env python3

from setuptools import setup

setup(
    name='LibAnt',
    packages=['libAnt', 'libAnt.profiles', 'libAnt.drivers', 'libAnt.loggers'],
    version='0.1.8',
    description='Python Ant+ Lib',
    author='Benjamin Tamasi',
    author_email='h@lfto.me',
    install_requires=['pyusb>=1.0.0', 'pyserial>=3.1.1'],
)
