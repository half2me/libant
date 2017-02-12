from threading import Lock

from libAnt.message import BroadcastMessage
from libAnt.profiles.power_profile import PowerProfileMessage
from libAnt.profiles.speed_cadence_profile import SpeedAndCadenceProfileMessage


class Factory:
    types = {
        121: SpeedAndCadenceProfileMessage,
        11: PowerProfileMessage
    }

    def __init__(self, callback=None):
        self._filter = None
        self._lock = Lock()
        self._messages = {}
        self._callback = callback

    def enableFilter(self):
        with self._lock:
            if self._filter is None:
                self._filter = {}

    def disableFilter(self):
        with self._lock:
            if self._filter is not None:
                self._filter = None

    def clearFilter(self):
        with self._lock:
            if self._filter is not None:
                self._filter.clear()

    def addToFilter(self, deviceNumber: int):
        with self._lock:
            if self._filter is not None:
                self._filter[deviceNumber] = True

    def removeFromFilter(self, deviceNumber: int):
        with self._lock:
            if self._filter is not None:
                if deviceNumber in self._filter:
                    del self._filter[deviceNumber]

    def parseMessage(self, msg: BroadcastMessage):
        with self._lock:
            if self._filter is not None:
                if msg.deviceNumber not in self._filter:
                    return
            if msg.deviceType in Factory.types:
                num = msg.deviceNumber
                type = msg.deviceType
                if type == 11: # Quick patch to filter out power messages with non-power info
                    if msg.content[0] != 16:
                        return
                pmsg = self.types[type](msg, self._messages[(num, type)] if (num, type) in self._messages else None)
                self._messages[(num, type)] = pmsg
                if callable(self._callback):
                    self._callback(pmsg)

    def reset(self):
        with self._lock:
            self._messages = {}