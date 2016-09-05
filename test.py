from libAnt.driver import USBDriver

driver = USBDriver(vid=0x0FCF, pid=0x1008)
with driver as d:
    buf = d.read(1)
    print(buf)