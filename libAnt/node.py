import threading
from queue import Queue, Empty

from libAnt.driver import Driver, DriverException
from libAnt.message import *


class Network:
    def __init__(self, key: bytes = b'\x00' * 8, name: str = None):
        self.key = key
        self.name = name
        self.number = 0

    def __str__(self):
        return self.name


class Pump(threading.Thread):
    def __init__(self, driver: Driver, out: Queue, onSucces, onFailure):
        super().__init__()
        self._stopper = threading.Event()
        self._driver = driver
        self._out = out
        self._waiters = []
        self._onSuccess = onSucces
        self._onFailure = onFailure

    def stop(self):
        self._stopper.set()

    def stopped(self):
        return self._stopper.isSet()

    def run(self):
        with self._driver as d:
            while not self._stopper.is_set():
                #  Write
                try:
                    outMsg = self._out.get(block=False)
                    self._waiters.append(outMsg)
                    d.write(outMsg)
                except Empty:
                    pass
                except DriverException:
                    self._stopper.set()
                    break

                # Read
                try:
                    msg = d.read()  # TODO: add timeout to driver
                    if msg.type == MESSAGE_CHANNEL_EVENT:
                        # This is a response to our outgoing message
                        for w in self._waiters:
                            if w.type == msg.content[1]:  # ACK
                                self._waiters.remove(w)
                                #  TODO: Call waiter callback from tuple (waiter, callback)
                                break
                    elif msg.type == MESSAGE_CHANNEL_BROADCAST_DATA:
                        bmsg = BroadcastMessage(msg.type, msg.content).build(msg.content)
                        try:
                            self._onSuccess(bmsg)
                        except Exception as e:
                            self._onFailure(e)

                except DriverException as e:
                    self._stopper.set()
                    self._onFailure(e)
                    break


class Node:
    def __init__(self, driver, name=None):
        self._driver = driver
        self._name = name
        self._out = Queue()
        self._pump = None
        self._configMessages = Queue()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self, onSuccess, onFailure):
        if not self.isRunning():
            self._pump = Pump(self._driver, self._out, onSuccess, onFailure)
            self._pump.start()

    def enableRxScanMode(self, networkKey=ANTPLUS_NETWORK_KEY, channelType=CHANNEL_TYPE_ONEWAY_RECEIVE,
                         frequency: int = 2457, rxTimestamp: bool = True, rssi: bool = True, channelId: bool = True):
        self._out.put(SystemResetMessage())
        self._out.put(SetNetworkKeyMessage(0, networkKey))
        self._out.put(AssignChannelMessage(0, channelType))
        self._out.put(SetChannelIdMessage(0))
        self._out.put(SetChannelRfFrequencyMessage(0, frequency))
        self._out.put(EnableExtendedMessagesMessage())
        self._out.put(LibConfigMessage(rxTimestamp, rssi, channelId))
        self._out.put(OpenRxScanModeMessage())

    def stop(self):
        if self.isRunning():
            self._pump.stop()
            self._pump.join()

    def isRunning(self):
        if self._pump is None:
            return False
        return self._pump.is_alive()

    def getCapabilities(self):
        pass
