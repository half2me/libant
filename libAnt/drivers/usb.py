from queue import Queue
from threading import Event, Thread

from usb import USBError, ENDPOINT_OUT, ENDPOINT_IN
from usb.control import get_interface
from usb.core import find
from usb.util import find_descriptor, endpoint_direction, claim_interface, dispose_resources

from libAnt.drivers.driver import Driver, DriverException
from libAnt.loggers.logger import Logger


class USBDriver(Driver):
    """
    An implementation of a USB ANT+ device driver
    """

    def __init__(self, vid, pid, logger: Logger = None):
        super().__init__(logger=logger)
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
                except USBError as e:
                    if e.errno not in (60, 110) and e.backend_error_code != -116:  # Timout errors
                        self._stopper.set()
            # We Put in an invalid byte so threads will realize the device is stopped
            self._queue.put(None)

    def _isOpen(self) -> bool:
        return self._driver_open

    def _open(self) -> None:
        print('USB OPEN START')
        try:
            # find the first USB device that matches the filter
            self._dev = find(idVendor=self._idVendor, idProduct=self._idProduct)

            if self._dev is None:
                raise DriverException("Could not open specified device")

            # Detach kernel driver
            try:
                if self._dev.is_kernel_driver_active(0):
                    try:
                        self._dev.detach_kernel_driver(0)
                    except USBError as e:
                        raise DriverException("Could not detach kernel driver")
            except NotImplementedError:
                pass  # for non unix systems

            # set the active configuration. With no arguments, the first
            # configuration will be the active one
            self._dev.set_configuration()

            # get an endpoint instance
            cfg = self._dev.get_active_configuration()
            self._interfaceNumber = cfg[(0, 0)].bInterfaceNumber
            interface = find_descriptor(cfg, bInterfaceNumber=self._interfaceNumber,
                                        bAlternateSetting=get_interface(self._dev,
                                                                        self._interfaceNumber))
            claim_interface(self._dev, self._interfaceNumber)

            self._epOut = find_descriptor(interface, custom_match=lambda e: endpoint_direction(
                e.bEndpointAddress) == ENDPOINT_OUT)

            self._epIn = find_descriptor(interface, custom_match=lambda e: endpoint_direction(
                e.bEndpointAddress) == ENDPOINT_IN)

            if self._epOut is None or self._epIn is None:
                raise DriverException("Could not initialize USB endpoint")

            self._queue = Queue()
            self._loop = self.USBLoop(self._epIn, self._packetSize, self._queue)
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
            dispose_resources(self._dev)
        except:
            pass
        self._dev = self._epOut = self._epIn = None
        self._driver_open = False
        print('USB CLOSE END')

    def _read(self, count: int, timeout=None) -> bytes:
        data = bytearray()
        for i in range(0, count):
            b = self._queue.get(timeout=timeout)
            if b is None:
                self._close()
                raise DriverException("Device is closed!")
            data.append(b)
        return bytes(data)

    def _write(self, data: bytes) -> None:
        return self._epOut.write(data)

    def _abort(self) -> None:
        pass  # not implemented for USB driver, use timeouts instead
