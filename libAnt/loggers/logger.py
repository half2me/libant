class Logger:
    def __init__(self, logFile: str):
        self._logFile = logFile
        self._log = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        def validate(logFile: str) -> str:
            if '.' in logFile:
                name, ext = logFile.split('.', 2)
                ext = '.' + ext
            else:
                name = logFile
                ext = ''
            num = 0
            exists = True
            while(exists):
                logFile = name + '-' + str(num) + ext
                try:
                    with open(logFile):
                            pass
                except IOError:
                    return logFile
                num += 1

        if self._log is not None:
            self.close()
        self._logFile = validate(self._logFile)
        self._log = open(self._logFile, 'wb')
        self.onOpen()

    def close(self):
        if self._log is not None:
            self.beforeClose()
            self._log.close()
            self.afterClose()

    def log(self, data: bytes):
        self._log.write(self.encodeData(data))

    def onOpen(self):
        pass

    def beforeClose(self):
        pass

    def afterClose(self):
        pass

    def encodeData(self, data):
        return data