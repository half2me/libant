#!/usr/bin/env python3
from time import sleep

from libAnt.driver import USBDriver
from libAnt.node import Node


def callback(msg):
    print(msg)
    print(msg.deviceNumber)


def eCallback(e):
    print('Error: ' + str(e))


with Node(USBDriver(vid=0x0FCF, pid=0x1008), 'MyNode') as n:
    n.enableRxScanMode()
    n.start(callback, eCallback)
    sleep(20)  # Listen for 20 sec
