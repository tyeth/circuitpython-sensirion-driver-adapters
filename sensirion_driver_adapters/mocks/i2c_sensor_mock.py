# -*- coding: utf-8 -*-
# (c) Copyright 2021 Sensirion AG, Switzerland

import logging
import random
import struct
from abc import ABC, abstractmethod

from sensirion_i2c_driver.crc_calculator import CrcCalculator

from sensirion_driver_adapters.i2c_adapter.i2c_channel import I2cChannel

logger = logging.getLogger(__name__)


class ResponseProvider(ABC):

    @abstractmethod
    def get_id(self) -> str:
        """Return an identifier of the response provider"""

    @abstractmethod
    def handle_command(self, cmd_id: int, data: bytes, response_length: int) -> bytes:
        """
        Provide a hook for sensor specific command handling.

        With specific implementation of this class, it becomes possible to emulate any sensor.

        :param cmd_id:
            Command id of the command to emulate.
        :param data:
            The parameters of the command. At this point the data do not contain a crc anymore.

        :response_length:
            The expected length of the returned bytes array.

        : return:
            An emulated response.
        """

    @staticmethod
    def random_bytes(data_length: int) -> bytes:
        """Compute a random data byte array of specified length"""
        return bytes(random.randint(0, 255) for i in range(data_length))

    @staticmethod
    def random_ascii_string(data_length: int) -> bytes:
        """Compute a random ascii data response."""
        return bytes(random.randint(32, 126) for i in range(data_length))

    @staticmethod
    def padded_ascii_string(string_value: str, nr_of_characters: int) -> bytes:
        """Pad an ascii-string with 0 to match the expected response length

        :params string_value:
            The string value that needs to be padded.

        :param nr_of_characters:
            The final length that is required.

        :returns:
            The prepared string buffer content.
        """
        return string_value.encode('ascii') + bytes([0] * (nr_of_characters - len(string_value)))


class RandomResponse(ResponseProvider):

    def get_id(self) -> str:
        return "random_default"

    def handle_command(self, cmd_id: int, data: bytes, response_length: int) -> bytes:
        return self.random_bytes(response_length)


class I2cSensorMock:
    """The sensor mock provides a base functionalities for mocking any kind of sensor.

    The responsibilities of the sensor mock are:
    - Check proper address
    - Check proper encoding of data stream. This includes the CRC check on reception and the
      encoding of returned data
    - Provide a hook for returning specific data that can be checked by the receiver
    """

    def __init__(self, i2c_address: int, crc: CrcCalculator, cmd_width: int = 2, id: int = 0) -> None:
        self._i2c_address = i2c_address
        self._cmd_width = cmd_width
        self._crc = crc
        self._id = id
        self._request_queue = []
        self._response_provider: ResponseProvider = RandomResponse()

    def register_response_provider(self, response_provider: ResponseProvider) -> None:
        self._response_provider = response_provider

    def write(self, address: int, data: bytes) -> None:
        assert address == self._i2c_address, "unsupported i2c address"
        # in case we have a wake up command, we may send only one byte of data
        cmd_len = min(len(data), self._cmd_width)
        cmd = struct.unpack(self.command_template(cmd_len), data[:cmd_len])[0]
        data = I2cChannel.strip_and_check_crc(bytearray(data[cmd_len:]), self._crc)
        self._request_queue.append((cmd, data))
        logger.info(f'device {self._response_provider.get_id()}-{self._id} received commands {cmd}')

    def read(self, address, nr_of_bytes_to_return) -> bytes:
        cmd, data = self._request_queue.pop(0)
        if nr_of_bytes_to_return <= 0:
            return bytes()
        nr_of_bytes = 2 * nr_of_bytes_to_return // 3
        assert address == self._i2c_address, "unsupported i2c address"
        logger.info(f'device {self._response_provider.get_id()}-{self._id} received'
                    f'read request for {nr_of_bytes} bytes')

        rx_data = self._response_provider.handle_command(cmd, data, nr_of_bytes)
        return I2cChannel.build_tx_data(rx_data, 0, self._crc)

    @staticmethod
    def command_template(cmd_width) -> str:
        return '>H' if cmd_width == 2 else '>B'
