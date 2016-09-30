#!/usr/bin/env python3
from time import sleep

from libAnt.driver import PcapDriver
from libAnt.node import Node


def callback(msg):
    print(msg)


def eCallback(e):
    raise e


with Node(PcapDriver('log.pcap'), 'MyNode') as n:
    # n.enableRxScanMode()
    n.start(callback, eCallback)
    sleep(1)  # Listen for 30sec
