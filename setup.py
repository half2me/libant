#!/usr/bin/env python3

from distutils.core import setup

setup(
    name='LibAnt',
    packages=['libAnt', 'libAnt.profiles'],
    version='0.1.3',
    description='Python Ant+ Lib',
    author='Benjamin Tamasi',
    author_email='h@lfto.me',
    url='https://github.com/half2me/libAnt',
    download_url='https://github.com/half2me/libAnt/tarball/0.1.3',
    keywords = ['ant', 'antplus', 'ant+', 'antfs', 'thisisant'],
    install_requires=['pyusb>=1.0.0', 'pyserial>=3.1.1'],
)
