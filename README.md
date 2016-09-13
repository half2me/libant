# LibAnt

[![Build Status](https://travis-ci.org/half2me/libant.svg?branch=master)](https://travis-ci.org/half2me/libant)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/half2me/libant/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/half2me/libant/?branch=master)
[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/half2me/libant/master/LICENSE) 
[![Join the chat at https://gitter.im/libant/Lobby](https://badges.gitter.im/libant/Lobby.svg)](https://gitter.im/libant/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)  
A Python implementation of the ANT+ Protocol  

The goal of this project is to provide a clean, Python-only implementation of the [ANT+ Protocol](https://www.thisisant.com). Usage of the library should require little to no knowledge of the ANT+ Protocol internals. It should be easy to use, easy to read, and have proper error handling.

This project was born when I decided to completely rewrite the [python-ant library](https://github.com/mvillalba/python-ant) from scratch, after not finding a fork that suited my needs. There were so many different forks of the original project, each with their own patches, but not a properly useable one. Because of this, there may be parts of the code which look similar to the python-ant library, as I have their code as a reference.

## Installing
For the stable version: `pip3 install antlib`  
For the latest clone the repo and do `./setup.py install` under UNIX systems or `python setup.py install` on windows (Make sure to use python3)

## Usage
See usage examples in the `demos` folder.