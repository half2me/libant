class Message:
    @classmethod
    def decode(cls, raw):
        if len(raw) < 2:
            raise Exception("Message is too short")
        msgId = raw[0]
        return Message()
