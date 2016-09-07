from libAnt.constants import *


class Message:
    def __init__(self, type: int, content: bytearray):
        self._type = type
        self._content = content

    def __len__(self):
        return len(self._content)

    def __iter__(self):
        return self._content

    def __str__(self):
        return '({:02X}): '.format(self._type) + ' '.join('{:02X}'.format(x) for x in self._content)

    def checksum(self) -> int:
        chk = MESSAGE_TX_SYNC ^ len(self) ^ self._type
        for b in self._content:
            chk ^= b
        return chk

    def encode(self) -> bytearray:
        b = bytearray()
        b.append(MESSAGE_TX_SYNC)
        b.append(len(self))
        b.append(self._type)
        b.extend(self._content)
        b.append(self.checksum())
        return b

    @property
    def type(self) -> int:
        return self._type

    @property
    def content(self) -> bytearray:
        return self._content


class SystemResetMessage(Message):
    def __init__(self):
        super().__init__(MESSAGE_SYSTEM_RESET, bytearray(1))


class SetNetworkKeyMessage(Message):
    def __init__(self, channel: int, key: bytes):
        content = bytearray()
        content.append(channel)
        content.extend(key)
        super().__init__(MESSAGE_NETWORK_KEY, content)


class AssignChannelMessage(Message):
    def __init__(self, channel: int, type: int, network: int = 0, extended: int = None):
        content = bytearray()
        content.append(channel)
        content.append(type)
        content.append(network)
        if extended is not None:
            content.append(extended)
        super().__init__(MESSAGE_CHANNEL_ASSIGN, content)


class SetChannelIdMessage(Message):
    def __init__(self, channel: int, deviceNumber: int = 0, deviceType: int = 0, transType: int = 0):
        content = bytearray()
        content.append(channel)
        content.extend(deviceNumber.to_bytes(2, byteorder='big'))
        content.append(deviceType)
        content.append(transType)
        super().__init__(MESSAGE_CHANNEL_ID, content)


class SetChannelRfFrequencyMessage(Message):
    def __init__(self, channel: int, frequency: int = 2457):
        content = bytearray()
        content.append(channel)
        content.append(frequency - 2400)
        super().__init__(MESSAGE_CHANNEL_FREQUENCY, content)


class OpenRxScanModeMessage(Message):
    def __init__(self):
        super().__init__(OPEN_RX_SCAN_MODE, bytearray(1))
