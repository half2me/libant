#!/usr/bin/env python3
from time import sleep

from libAnt.driver import USBDriver
from libAnt.message import SetNetworkKeyMessage
from libAnt.node import Node, SystemResetMessage


def callback(msg):
    print(msg)
    print(msg.deviceNumber)


def eCallback(e):
    print('Error: ' + str(e))


driver = USBDriver(vid=0x0FCF, pid=0x1008)
with Node(driver, 'MyNode') as n:
    n.enableRxScanMode()
    n.start(callback, eCallback)
    sleep(10)
