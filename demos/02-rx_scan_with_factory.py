#!/usr/bin/env python3
from time import sleep

from libAnt.driver import USBDriver
from libAnt.node import Node
from libAnt.profiles.factory import Factory


def callback(msg):
    print(msg)


def eCallback(e):
    print(e)


with Node(USBDriver(vid=0x0FCF, pid=0x1008), 'MyNode') as n:
    f = Factory(callback)

    n.enableRxScanMode()
    n.start(f.parseMessage, eCallback)
    sleep(60)  # Listen for 1min
