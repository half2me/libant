#!/usr/bin/env python3
from time import sleep

from libAnt.drivers.usb import USBDriver
from libAnt.loggers.pcap import PcapLogger
from libAnt.node import Node
from libAnt.profiles.factory import Factory


def callback(msg):
    print(msg)


def eCallback(e):
    raise (e)


with Node(USBDriver(vid=0x0FCF, pid=0x1008, logger=PcapLogger(logFile='log.pcap')), 'MyNode') as n:
    f = Factory(callback)

    n.enableRxScanMode()
    n.start(f.parseMessage, eCallback)
    sleep(10)  # Listen for 1min
