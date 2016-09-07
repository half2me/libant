from libAnt.constants import MESSAGE_TX_SYNC


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
