from abc import abstractmethod
from threading import Lock
from serial import Serial, SerialException, SerialTimeoutException

import usb


class Driver:
    def __init__(self):
        self._lock = Lock()

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
    def __init__(self, device, baudRate=115200):
        super().__init__()
        self._device = device
        self._baudRate = baudRate
        self._serial = None

    def _isOpen(self):
        return self._serial is None

    def _open(self):
        try:
            self._dev = Serial(self._device, self._baudRate)
        except SerialException as e:
            raise e  # TODO: Make DriverException

    def _close(self):
        pass

    def _write(self, data):
        pass

    def _read(self, count):
        pass


class USB2Driver(Driver):
    def __init__(self, idVendor, idProduct):
        Driver.__init__(self)
        self._idVendor = idVendor
        self._idProduct = idProduct
        self._dev = None
        self._epOut = None
        self._epIn = None
        self._interfaceNumber = None

    def _open(self):
        self._dev = usb.core.find(idVendor=self._idVendor, idProduct=self._idProduct)
        if self._dev is None:
            pass  # # TODO: Make DriverException

        # take care of bugs with the kernel driver
        if self._dev.is_kernel_driver_active(0):
            try:
                self._dev.detach_kernel_driver(0)
            except usb.USBError as e:
                pass  # TODO: Make DriverException

        self._dev.set_configuration()
        cfg = self._dev.get_active_configuration()
        self._interfaceNumber = cfg[(0, 0)].bInterfaceNumber
        interface = usb.util.find_descriptor(cfg, bInterfaceNumber=self._interfaceNumber,
                                             bAlternateSetting=usb.control.get_interface(self._dev,
                                                                                         self._interfaceNumber))
        usb.util.claim_interface(self._dev, self._interfaceNumber)

        self._epOut = usb.util.find_descriptor(interface, custom_match=lambda e: usb.util.endpoint_direction(
            e.bEndpointAddress) == usb.ENDPOINT_OUT)
        assert self._epOut is not None  # TODO: Make DriverException

        self._ep_in = usb.util.find_descriptor(interface, custom_match=lambda e: usb.util.endpoint_direction(
            e.bEndpointAddress) == usb.ENDPOINT_IN)
        assert self._ep_in is not None  # TODO: Make DriverException
