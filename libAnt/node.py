import threading


class Network:
    def __init__(self, key=b'\x00' * 8, name=None):
        self.key = key
        self.name = name
        self.number = 0

    def __str__(self):
        return self.name + self.key


class Pump(threading.Thread):
    def __init__(self):
        super().__init__()
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        pass


class Node:
    def __init__(self, driver, name=None):
        self._driver = driver
        self._name = name
        self.running = False
        self.pump = Pump()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        if not self.running:
            self.pump.start()
            self.running = True

    def stop(self):
        if self.running:
            self.pump.stop()
            self.pump.join()
            self.running = False

    def reset(self):
        pass

    def getCapabilities(self):
        pass

    def addEventListener(self, callback):
        pass
