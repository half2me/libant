class Node():
    def __init__(self, driver, name=None):
        with driver:
            self._driver = driver
        self._name = name

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        pass

    def stop(self):
        pass

    def reset(self):
        pass

    def getCapabilities(self):
        pass

    def addEventListener(self, callback):
        pass