#!/usr/bin/env python3
from libAnt.constants import ANTPLUS_NETWORK_KEY
from libAnt.driver import USBDriver

driver = USBDriver(vid=0x0FCF, pid=0x1008)
with driver as d:
    msg = bytearray()
    msg.append(0x00) # net number
    msg.extend(ANTPLUS_NETWORK_KEY)
    d.write(0x46, msg)  # system reset
    print(d.read(1))
