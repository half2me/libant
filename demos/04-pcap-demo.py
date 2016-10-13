#!/usr/bin/env python3
from time import sleep

from libAnt.driver import PcapDriver, PcapLogger
from libAnt.node import Node
from libAnt.profiles.factory import Factory


def callback(msg):
    print(msg)


def eCallback(e):
    print(e)


with Node(PcapDriver('log.pcap', PcapLogger("pcap-demo-log.pcap")), 'MyNode') as n:
    # n.enableRxScanMode()
    f = Factory(callback)
    n.start(f.parseMessage, eCallback)
    sleep(20)  # Listen for 30sec
