from copy import deepcopy

import time

from libAnt.message import BroadcastMessage


class ProfileMessage:
    def __init__(self, msg, previous):
        self.previous = previous
        self.msg = deepcopy(msg)
        self.count = previous.count + 1 if previous is not None else 1
        self.timestamp = time.time()
        self.firstTimestamp = previous.firstTimestamp if previous is not None else self.timestamp

    def __str__(self):
        return str(self.msg.deviceNumber)

    @staticmethod
    def decode(cls, msg: BroadcastMessage):
        if msg.deviceType in cls.match:
            cls.match[msg.deviceType]()