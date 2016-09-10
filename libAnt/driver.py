from abc import abstractmethod
from queue import Queue
from threading import Lock, Thread, Event

from serial import Serial, SerialException, SerialTimeoutException

import usb

from libAnt.constants import MESSAGE_TX_SYNC
from libAnt.message import Message, SystemResetMessage


class DriverException(Exception):
    pass


class Driver:
    """
    The driver provides an interface to read and write raw data to and from an ANT+ capable hardware device
    """

    def __init__(self):
        self._lock = Lock()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def isOpen(self) -> bool:
        with self._lock:
            return self._isOpen()

    def open(self) -> None:
        with self._lock:
            if not self._isOpen():
                self._open()

    def close(self) -> None:
        with self._lock:
            if self._isOpen:
                self._close()

    def reOpen(self) -> None:
        with self._lock:
            if self._isOpen():
                self._close()
            self._open()

    def read(self) -> Message:
        if not self.isOpen():
            raise DriverException("Device is closed")

        with self._lock:
            while True:
                sync = self._read(1)[0]
                if sync is not MESSAGE_TX_SYNC:
                    continue
                len = self._read(1)[0]
                type = self._read(1)[0]
                data = self._read(len)
                chk = self._read(1)[0]
                msg = Message(type, data)
                if msg.checksum() == chk:
                    return msg

    def write(self, msg: Message) -> None:
        if not self.isOpen():
            raise DriverException("Device is closed")

        with self._lock:
            self._write(msg.encode())

    @abstractmethod
    def _isOpen(self) -> bool:
        pass

    @abstractmethod
    def _open(self) -> None:
        pass

    @abstractmethod
    def _close(self) -> None:
        pass

    @abstractmethod
    def _read(self, count: int) -> bytes:
        pass

    @abstractmethod
    def _write(self, data: bytes) -> None:
        pass


class SerialDriver(Driver):
    """
    An implementation of a serial ANT+ device driver
    """

    def __init__(self, device: str, baudRate: int = 115200):
        super().__init__()
        self._device = device
        self._baudRate = baudRate
        self._serial = None

    def __str__(self):
        if self.isOpen():
            return self._device + " @ " + str(self._baudRate)
        return None

    def _isOpen(self) -> bool:
        return self._serial is None

    def _open(self) -> None:
        try:
            self._serial = Serial(self._device, self._baudRate)
        except SerialException as e:
            raise DriverException(str(e))

        if not self._serial.isOpen():
            raise DriverException("Could not open specified device")

    def _close(self) -> None:
        self._serial.close()
        self._serial = None

    def _read(self, count: int) -> bytes:
        return self._serial.read(count)

    def _write(self, data: bytes) -> None:
        try:
            self._serial.write(data)
            self._serial.flush()
        except SerialTimeoutException as e:
            raise DriverException(str(e))


class USBDriver(Driver):
    """
    An implementation of a USB ANT+ device driver
    """

    def __init__(self, vid, pid):
        Driver.__init__(self)
        self._idVendor = vid
        self._idProduct = pid
        self._dev = None
        self._epOut = None
        self._epIn = None
        self._interfaceNumber = None
        self._packetSize = 0x20
        self._queue = None
        self._loop = None
        self._driver_open = False

    def __str__(self):
        if self.isOpen():
            return str(self._dev)
        return "Closed"

    def _isOpen(self) -> bool:
        return self._driver_open

    def _open(self) -> None:
        print('USB OPEN START')
        try:
            # find the first USB device that matches the filter
            self._dev = usb.core.find(idVendor=self._idVendor, idProduct=self._idProduct)

            if self._dev is None:
                raise DriverException("Could not open specified device")

            # Detach kernel driver
            try:
                if self._dev.is_kernel_driver_active(0):
                    try:
                        self._dev.detach_kernel_driver(0)
                    except usb.USBError as e:
                        raise DriverException("Could not detach kernel driver")
            except NotImplementedError:
                pass  # for non unix systems

            # set the active configuration. With no arguments, the first
            # configuration will be the active one
            self._dev.set_configuration()

            # get an endpoint instance
            cfg = self._dev.get_active_configuration()
            self._interfaceNumber = cfg[(0, 0)].bInterfaceNumber
            interface = usb.util.find_descriptor(cfg, bInterfaceNumber=self._interfaceNumber,
                                                 bAlternateSetting=usb.control.get_interface(self._dev,
                                                                                             self._interfaceNumber))
            usb.util.claim_interface(self._dev, self._interfaceNumber)

            self._epOut = usb.util.find_descriptor(interface, custom_match=lambda e: usb.util.endpoint_direction(
                e.bEndpointAddress) == usb.ENDPOINT_OUT)

            self._epIn = usb.util.find_descriptor(interface, custom_match=lambda e: usb.util.endpoint_direction(
                e.bEndpointAddress) == usb.ENDPOINT_IN)

            if self._epOut is None or self._epIn is None:
                raise DriverException("Could not initialize USB endpoint")

            self._queue = Queue()
            self._loop = USBLoop(self._epIn, self._packetSize, self._queue)
            self._loop.start()
            self._driver_open = True
            print('USB OPEN SUCCESS')
        except IOError as e:
            self._close()
            raise DriverException(str(e))

    def _close(self) -> None:
        print('USB CLOSE START')
        if self._loop is not None:
            if self._loop.is_alive():
                self._loop.stop()
                self._loop.join()
        self._loop = None
        try:
            self._dev.reset()
            usb.util.dispose_resources(self._dev)
        except:
            pass
        self._dev = self._epOut = self._epIn = None
        self._driver_open = False
        print('USB CLOSE END')

    def _read(self, count: int) -> bytes:
        data = bytearray()
        for i in range(0, count):
            b = self._queue.get()
            if b is None:
                self._close()
                raise DriverException("Device is closed!")
            data.append(b)
        return bytes(data)

    def _write(self, data: bytes) -> None:
        return self._epOut.write(data)


class USBLoop(Thread):
    def __init__(self, ep, packetSize: int, queue: Queue):
        super().__init__()
        self._stopper = Event()
        self._ep = ep
        self._packetSize = packetSize
        self._queue = queue

    def stop(self) -> None:
        self._stopper.set()

    def run(self) -> None:
        while not self._stopper.is_set():
            try:
                data = self._ep.read(self._packetSize, timeout=1000)
                for d in data:
                    self._queue.put(d)
            except usb.core.USBError as e:
                if e.errno not in (60, 110) and e.backend_error_code != -116: # Timout errors
                    self._stopper.set()
        #  We Put in an invalid byte so threads will realize the device is stopped
        self._queue.put(None)
