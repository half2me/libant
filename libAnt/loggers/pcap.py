from struct import Struct
import time
import math

from libAnt.loggers.logger import Logger

class PcapLogger(Logger):
    def onOpen(self):
        # write pcap global header
        magic_number = b'\xD4\xC3\xB2\xA1'
        version_major = 2
        version_minor = 4
        thiszone = b'\x00\x00\x00\x00'
        sigfigs = b'\x00\x00\x00\x00'
        snaplen = b'\xFF\x00\x00\x00'
        network = b'\x01\x00\x00\x00'
        pcap_global_header = Struct('<4shh4s4s4s4s')
        self._log.write(
            pcap_global_header.pack(magic_number, version_major, version_minor, thiszone, sigfigs,
                                    snaplen, network))

    def encodeData(self, data):
        timestamp = time.time()
        frac, whole = math.modf(timestamp)

        ts_sec = int(whole).to_bytes(4, byteorder='little')
        ts_usec = int(frac * 1000 * 1000).to_bytes(4, byteorder='little')
        incl_len = len(data)
        orig_len = incl_len

        pcap_packet_header = Struct('<4s4sll').pack(ts_sec, ts_usec, incl_len, orig_len)
        return pcap_packet_header + data