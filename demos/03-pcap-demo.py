#!/usr/bin/env python3
from time import sleep

from libAnt.drivers.pcap import PcapDriver
from libAnt.node import Node
from libAnt.profiles.factory import Factory


def callback(msg):
    print(msg)


def eCallback(e):
    print(e)


with Node(PcapDriver('demo-capture-1.pcap'), 'PcapNode1') as n:
    # n.enableRxScanMode() # Pcap driver is read-only
    f = Factory(callback)
    n.start(f.parseMessage, eCallback)
    sleep(30)  # Listen for 30sec
