#!/usr/bin/env python3
from time import sleep

from libAnt.drivers.serial import SerialDriver
from libAnt.drivers.usb import USBDriver
from libAnt.node import Node


def callback(msg):
    print(msg)


def eCallback(e):
    print(e)

# for USB driver
# with Node(USBDriver(vid=0x0FCF, pid=0x1008), 'MyNode') as n:

# for serial driver
with Node(SerialDriver("/dev/ttyUSB0"), 'MyNode') as n:
    n.enableRxScanMode()
    n.start(callback, eCallback)
    sleep(3)  # Listen for 30sec
