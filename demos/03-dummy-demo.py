#!/usr/bin/env python3
from time import sleep

from libAnt.driver import DummyDriver
from libAnt.node import Node


def callback(msg):
    print(msg)


def eCallback(e):
    print(e)


with Node(DummyDriver(), 'MyNode') as n:
    n.enableRxScanMode()
    n.start(callback, eCallback)
    sleep(30)  # Listen for 30sec
