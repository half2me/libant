#!/usr/bin/env python3
from time import sleep

from libAnt.driver import PcapDriver, PcapLogger
from libAnt.node import Node


def callback(msg):
    print(msg)


def eCallback(e):
    raise e


with Node(PcapDriver('log.pcap', logger=PcapLogger(logFile='pcapdriverlog.pcap')), 'MyNode') as n:
    # n.enableRxScanMode()
    n.start(callback, eCallback)
    sleep(20)  # Listen for 30sec
