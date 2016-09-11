from copy import deepcopy

from libAnt.message import BroadcastMessage


class ProfileMessage:
    def __init__(self, msg, previous):
        self.previous = previous
        self.msg = deepcopy(msg)

    def __str__(self):
        return str(self.msg.deviceNumber)

    @staticmethod
    def decode(cls, msg: BroadcastMessage):
        if msg.deviceType in cls.match:
            cls.match[msg.deviceType]()