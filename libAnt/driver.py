from abc import abstractmethod
from threading import Lock

from serial import Serial, SerialException, SerialTimeoutException

import usb


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

    def isOpen(self):
        with self._lock:
            return self._isOpen()

    def open(self):
        with self._lock:
            if not self._isOpen():
                self._open()

    def close(self):
        with self._lock:
            if self._isOpen():
                self._close()

    def reOpen(self):
        with self._lock:
            if self._isOpen():
                self._close()
                self._open()

    def read(self, count):
        if count <= 0:
            raise DriverException("Count must be > 0")
        if not self.isOpen():
            raise DriverException("Device is closed")

        with self._lock:
            return self._read(count)

    def write(self, msg):
        if not self.isOpen():
            raise DriverException("Device is closed")

        with self._lock:
            self.write(msg)

    @abstractmethod
    def _isOpen(self):
        pass

    @abstractmethod
    def _open(self):
        pass

    @abstractmethod
    def _close(self):
        pass

    @abstractmethod
    def _read(self, count):
        pass

    @abstractmethod
    def _write(self, data):
        pass


class SerialDriver(Driver):
    """
    An implementation of a serial ANT+ device driver
    """

    def __init__(self, device, baudRate=115200):
        super().__init__()
        self._device = device
        self._baudRate = baudRate
        self._serial = None

    def __str__(self):
        if self.isOpen():
            return self._device + " @ " + str(self._baudRate)
        return None

    def _isOpen(self):
        return self._serial is None

    def _open(self):
        try:
            self._serial = Serial(self._device, self._baudRate)
        except SerialException as e:
            raise DriverException(str(e))

        if not self._serial.isOpen():
            raise DriverException("Could not open specified device")

    def _close(self):
        self._serial.close()
        self._serial = None

    def _read(self, count):
        return self._serial.read(count)

    def _write(self, data):
        try:
            count = self._serial.write(data)
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

    def __str__(self):
        if self.isOpen():
            return str(self._dev)
        return "Closed"

    def _isOpen(self):
        return self._dev is not None

    def _open(self):
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
        except IOError as e:
            raise DriverException(str(e))

    def _close(self):
        usb.util.release_interface(self._dev, self._interfaceNumber)
        usb.util.dispose_resources(self._dev)
        self._dev = self._epOut = self._epIn = None

    def _read(self, count):
        return self._epIn.read(count, timeout=-1)  # wait as long as it takes :)

    def _write(self, data):
        return self._epOut.write(data)
