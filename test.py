#!/usr/bin/env python3
from libAnt.constants import ANTPLUS_NETWORK_KEY, MESSAGE_NETWORK_KEY, MESSAGE_SYSTEM_RESET
from libAnt.driver import USBDriver
from libAnt.message import *

driver = USBDriver(vid=0x0FCF, pid=0x1008)
with driver as d:
    d.write(SystemResetMessage())
    print(d.read())

    d.write(SetNetworkKeyMessage(0, ANTPLUS_NETWORK_KEY))
    print(d.read())

    d.write(AssignChannelMessage(0, CHANNEL_TYPE_ONEWAY_RECEIVE))
    print(d.read())

    d.write(SetChannelIdMessage(0))
    print(d.read())

    d.write(SetChannelRfFrequencyMessage(0))
    print(d.read())

    #TODO:  Ext messages here
    d.write(EnableExtendedMessagesMessage())
    print(d.read())

    d.write(OpenRxScanModeMessage())
    print(d.read())

    while True:
        print(d.read())