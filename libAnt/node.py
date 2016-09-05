import threading
from time import sleep

from libAnt.constants import MESSAGE_TX_SYNC, MESSAGE_TX_SYNC_LEGACY
from libAnt.message import Message


class Network:
    def __init__(self, key=b'\x00' * 8, name=None):
        self.key = key
        self.name = name
        self.number = 0

    def __str__(self):
        return self.name + self.key


class Pump(threading.Thread):
    def __init__(self, driver):
        super().__init__()
        self._stop = threading.Event()
        self._driver = driver

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        with self._driver as driver:
            while not self._stop.is_set():
                sync = driver.read(1)  # search for sync
                print(sync)
                if sync == MESSAGE_TX_SYNC or sync == MESSAGE_TX_SYNC_LEGACY:
                    size = driver.read(1) # get size of message
                    try:
                        raw = bytearray(sync)
                        raw.extend(size)
                        raw.extend(driver.read(size + 2))
                        message = Message.decode(raw)
                    except Exception as e:
                        pass


class Node:
    def __init__(self, driver, name=None):
        self._driver = driver
        self._name = name
        self._pump = Pump(driver)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        if not self.isRunning():
            self._pump.start()

    def stop(self):
        if self.isRunning():
            self._pump.stop()
            self._pump.join()

    def isRunning(self):
        return self._pump.is_alive()

    def reset(self):
        self.stop()
        # TODO: reset device

    def getCapabilities(self):
        pass
