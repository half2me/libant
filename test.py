#!/usr/bin/env python3
from time import sleep

from libAnt.driver import USBDriver
from libAnt.node import Node

err = False

def callback(msg):
    print(msg)
    print(msg.deviceNumber)


def eCallback(e):
    global err
    err = True
    print('Error: ' + str(e))

while True:
    with Node(USBDriver(vid=0x0FCF, pid=0x1008), 'MyNode') as n:
        err = False
        print('Opening node...')
        n.enableRxScanMode()
        n.start(callback, eCallback)
        while not err:
            sleep(1)