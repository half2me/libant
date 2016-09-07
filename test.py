#!/usr/bin/env python3
from libAnt.constants import ANTPLUS_NETWORK_KEY, MESSAGE_NETWORK_KEY
from libAnt.driver import USBDriver
from libAnt.message import Message

driver = USBDriver(vid=0x0FCF, pid=0x1008)
with driver as d:
    msg = Message(MESSAGE_NETWORK_KEY, ANTPLUS_NETWORK_KEY)
    print(msg)
    d.write(msg)  # system
    ret = d.read()
    print(ret)

