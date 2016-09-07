from libAnt.constants import MESSAGE_TX_SYNC
from libAnt.driver import USBDriver

driver = USBDriver(vid=0x0FCF, pid=0x1008)
with driver as d:
    payload = bytearray()
    payload.append(MESSAGE_TX_SYNC)
    payload.append(0x4A)
    payload.append(0x01)
    payload.append(0x00)
    chksum = [for b in payload]
    payload.append()
    print(payload)
    d.write(payload)
    print("yolo")
