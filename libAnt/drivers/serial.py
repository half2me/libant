from queue import Queue
from threading import Thread, Event

from serial import Serial
from serial import SerialTimeoutException, SerialException

from libAnt.drivers.driver import Driver, DriverException
from libAnt.loggers.logger import Logger


class SerialDriver(Driver):
    """
    An implementation of a serial ANT+ device driver
    """

    def __init__(self, device: str, baudRate: int = 115200, logger: Logger = None):
        super().__init__(logger=logger)
        self._device = device
        self._baudRate = baudRate
        self._serial = None

    def __str__(self):
        if self.isOpen():
            return self._device + " @ " + str(self._baudRate)
        return None

    def _isOpen(self) -> bool:
        return self._serial is not None

    def _open(self) -> None:
        try:
            self._serial = Serial(port=self._device, baudrate=self._baudRate)
        except SerialException as e:
            raise DriverException(str(e))

        if not self._serial.isOpen():
            raise DriverException("Could not open specified device")

    def _close(self) -> None:
        self._serial.close()
        self._serial = None

    def _read(self, count: int, timeout=None) -> bytes:
        return self._serial.read(count)

    def _write(self, data: bytes) -> None:
        try:
            self._serial.write(data)
            self._serial.flush()
        except SerialTimeoutException as e:
            raise DriverException(str(e))

    def _abort(self) -> None:
        if self._serial is not None:
            self._serial.cancel_read()
            self._serial.cancel_write()
            self._serial.reset_input_buffer()
            self._serial.reset_output_buffer()