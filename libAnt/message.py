from libAnt.constants import *


class Message:
    def __init__(self, type: int, content: bytes):
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

    def encode(self) -> bytes:
        b = bytearray([MESSAGE_TX_SYNC, len(self), self._type])
        b.extend(self._content)
        b.append(self.checksum())
        return bytes(b)

    @property
    def type(self) -> int:
        return self._type

    @property
    def content(self) -> bytes:
        return self._content


class BroadcastMessage(Message):
    def __init__(self, type: int, content: bytes):
        self.flag = None
        self.deviceNumber = self.deviceType = self.transType = None
        self.rssiMeasurementType = self.rssi = self._rssiThreshold = None
        self.rssi = None
        self.rssiThreshold = None
        self.rxTimestamp = None
        self.channel = None
        self.extendedContent = None

        super().__init__(type, content)

    def build(self, raw: bytes):
        self._type = MESSAGE_CHANNEL_BROADCAST_DATA
        self.channel = raw[0]
        self._content = raw[1:9]
        if len(raw) > 9:  # Extended message
            self.flag = raw[9]
            self.extendedContent = raw[10:]
            offset = 0
            if self.flag & EXT_FLAG_CHANNEL_ID:
                self.deviceNumber = int.from_bytes(self.extendedContent[:2], byteorder='little', signed=False)
                self.deviceType = self.extendedContent[2]
                self.transType = self.extendedContent[3]
                offset += 4
            if self.flag & EXT_FLAG_RSSI:
                rssi = self.extendedContent[offset:(offset + 3)]
                self.rssiMeasurementType = rssi[0]
                self.rssi = rssi[1]
                self.rssiThreshold = rssi[2]
                offset += 3
            if self.flag & EXT_FLAG_TIMESTAMP:
                self.rxTimestamp = int.from_bytes(self.extendedContent[offset:],
                                                  byteorder='little', signed=False)
        return self

    def checksum(self) -> int:
        pass

    def encode(self) -> bytes:
        pass


class SystemResetMessage(Message):
    def __init__(self):
        super().__init__(MESSAGE_SYSTEM_RESET, b'0')


class SetNetworkKeyMessage(Message):
    def __init__(self, channel: int, key: bytes = ANTPLUS_NETWORK_KEY):
        content = bytearray([channel])
        content.extend(key)
        super().__init__(MESSAGE_NETWORK_KEY, bytes(content))


class AssignChannelMessage(Message):
    def __init__(self, channel: int, type: int, network: int = 0, extended: int = None):
        content = bytearray([channel, type, network])
        if extended is not None:
            content.append(extended)
        super().__init__(MESSAGE_CHANNEL_ASSIGN, bytes(content))


class SetChannelIdMessage(Message):
    def __init__(self, channel: int, deviceNumber: int = 0, deviceType: int = 0, transType: int = 0):
        content = bytearray([channel])
        content.extend(deviceNumber.to_bytes(2, byteorder='big'))
        content.append(deviceType)
        content.append(transType)
        super().__init__(MESSAGE_CHANNEL_ID, bytes(content))


class SetChannelRfFrequencyMessage(Message):
    def __init__(self, channel: int, frequency: int = 2457):
        content = bytes([channel, frequency - 2400])
        super().__init__(MESSAGE_CHANNEL_FREQUENCY, content)


class OpenRxScanModeMessage(Message):
    def __init__(self):
        super().__init__(OPEN_RX_SCAN_MODE, bytes([0]))


class EnableExtendedMessagesMessage(Message):
    def __init__(self, enable: bool = True):
        content = bytes([0, int(enable)])
        super().__init__(MESSAGE_ENABLE_EXT_RX_MESSAGES, content)


class LibConfigMessage(Message):
    def __init__(self, rxTimestamp: bool = True, rssi: bool = True, channelId: bool = True):
        config = 0
        if rxTimestamp:
            config |= EXT_FLAG_TIMESTAMP
        if rssi:
            config |= EXT_FLAG_RSSI
        if channelId:
            config |= EXT_FLAG_CHANNEL_ID
        super().__init__(MESSAGE_LIB_CONFIG, bytes([0, config]))
