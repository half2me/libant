import time
from queue import Queue
from struct import unpack, error
from threading import Thread, Event

from libAnt.drivers.driver import Driver
from libAnt.loggers.logger import Logger


class PcapDriver(Driver):
    def __init__(self, pcap : str, logger: Logger = None):
        super().__init__(logger=logger)
        self._isopen = False
        self._pcap = pcap
        self._buffer = Queue()

        self._loop = None

    class PcapLoop(Thread):
        def __init__(self, pcap, buffer: Queue):
            super().__init__()
            self._stopper = Event()
            self._pcap = pcap
            self._buffer = buffer

        def stop(self) -> None:
            self._stopper.set()

        def run(self) -> None:
            self._pcapfile = open(self._pcap, 'rb')
            # move file pointer to first packet header
            global_header_length = 24
            self._pcapfile.seek(global_header_length, 0)

            first_ts = 0
            start_time = time.time()
            while not self._stopper.is_set():
                try:
                    ts_sec, = unpack('i', self._pcapfile.read(4))
                except error:
                    break
                ts_usec = unpack('i', self._pcapfile.read(4))[0] / 1000000

                if first_ts is 0:
                    first_ts = ts_sec + ts_usec

                ts = ts_sec + ts_usec
                send_time = ts - first_ts
                elapsed_time = time.time() - start_time
                if send_time > (elapsed_time):
                    sleep_time = send_time - elapsed_time
                    time.sleep(sleep_time)

                packet_length = unpack('i', self._pcapfile.read(4))[0]
                self._pcapfile.seek(4, 1)
                for i in range(packet_length):
                    self._buffer.put(self._pcapfile.read(1))

            self._pcapfile.close()

    def _isOpen(self) -> bool:
        return self._isopen

    def _open(self) -> None:
        self._isopen = True
        self._loop = self.PcapLoop(self._pcap, self._buffer)
        self._loop.start()

    def _close(self) -> None:
        self._isopen = False
        if self._loop is not None:
            if self._loop.is_alive():
                self._loop.stop()
                self._loop.join()
        self._loop = None

    def _read(self, count: int, timeout=None) -> bytes:
        result = bytearray()

        while len(result) < count:
            result += self._buffer.get(block=True, timeout=timeout)

        return bytes(result)

    def _write(self, data: bytes) -> None:
        pass
