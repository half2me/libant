#!/usr/bin/env python3
from libAnt.constants import ANTPLUS_NETWORK_KEY, MESSAGE_NETWORK_KEY, MESSAGE_SYSTEM_RESET
from libAnt.driver import USBDriver
from libAnt.message import Message

driver = USBDriver(vid=0x0FCF, pid=0x1008)
with driver as d:
    b = bytearray()
    b.append(0)
    b.extend(ANTPLUS_NETWORK_KEY)
    msg = Message(MESSAGE_NETWORK_KEY, b)
    print(msg)
    d.write(msg)
    ret = d.read()
    print(ret)

