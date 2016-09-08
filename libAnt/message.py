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
    def __init__(self, channel: int, content: bytes):
        c = bytearray([channel])
        c.extend(content[:8])
        if len(content) > 8:  # Extended message
            self._flag = content[8]
            self._extendedContent = content[len(content) - 9:]
            offset = 0
            if self._flag & EXT_FLAG_CHANNEL_ID:
                self._deviceNumber = int.from_bytes(self._extendedContent[:2], byteorder='little', signed=False)
                self._deviceType = self._extendedContent[2]
                self._transType = self._extendedContent[3]
                offset += 4
            if self._flag & EXT_FLAG_RSSI:
                rssi = self._extendedContent[len(self._extendedContent) - offset:]
                self._rssiMeasurementType = rssi[0]
                self._rssi = rssi[1]
                self._rssiThreshold = rssi[2]
                offset += 3
            if self._flag & EXT_FLAG_TIMESTAMP:
                self._rxTimestamp = int.from_bytes(self._extendedContent[len(self._extendedContent) - offset:],
                                                   byteorder='little', signed=False)

        super().__init__(MESSAGE_CHANNEL_BROADCAST_DATA, bytes(c))

    def __str__(self):
        pass

    def checksum(self) -> int:
        pass

    def encode(self) -> bytes:
        pass


class SystemResetMessage(Message):
    def __init__(self):
        super().__init__(MESSAGE_SYSTEM_RESET, b'0')


class SetNetworkKeyMessage(Message):
    def __init__(self, channel: int, key: bytes):
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