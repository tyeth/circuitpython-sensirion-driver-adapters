# -*- coding: utf-8 -*-
# (c) Copyright 2021 Sensirion AG, Switzerland
import struct
from typing import Optional

import pytest
from sensirion_i2c_driver import CrcCalculator
from sensirion_i2c_driver import SensirionI2cCommand

from sensirion_driver_adapters.i2c_adapter.i2c_channel import I2cChannel
from sensirion_driver_adapters.transfer import Transfer, execute_transfer
from sensirion_driver_adapters.rx_tx_data import TxData, RxData
from tests.i2c_device_mocks import I2cProgrammerMock


class TestResultProvider:

    def __init__(self, data_array):
        self._data = data_array

    def write(self, address, data):
        ...

    def read(self, address, length):
        data_length = length // 3 * 2
        return struct.pack(f'>{data_length}B', *self._data)


class DummyConnection:

    def __init__(self, expected_tx_data):
        self._expected_tx_data = expected_tx_data

    def execute(self, address, request):
        address += 1
        assert request.tx_data == self._expected_tx_data


class VerificationCommand1(SensirionI2cCommand):
    """
    Command to verify channel
    """

    def __init__(self, command=0xABCD, tx_data=None):
        super().__init__(command, tx_data=tx_data,
                         crc=CrcCalculator(8, 0x31, 0xFF, 0x00),
                         read_delay=0.0, timeout=0,
                         rx_length=0)


def test_command_no_additional_parameters():
    class TransferNoParameters(Transfer):
        def pack(self) -> Optional[bytes]:
            return self.tx_data.pack()

        tx = TxData(cmd_id=0xABCD, descriptor='>H')

    tc = VerificationCommand1()
    connection = DummyConnection(tc.tx_data)  # write the packed data to the connection
    channel = I2cChannel(connection, crc=CrcCalculator(8, 0x31, 0xFF, 0x00))
    execute_transfer(channel, TransferNoParameters())


def test_command_one_byte_parameter():
    class TransferOneParameter(Transfer):
        def __init__(self, my_param):
            self._my_param = my_param

        def pack(self) -> Optional[bytearray]:
            return self.tx_data.pack([self._my_param])

        tx = TxData(cmd_id=0xABCD, descriptor='>HB')

    tc = VerificationCommand1(tx_data=struct.pack('B', 1))
    connection = DummyConnection(tc.tx_data)
    channel = I2cChannel(connection, crc=CrcCalculator(8, 0x31, 0xFF, 0x00))
    execute_transfer(channel, TransferOneParameter(my_param=1))


def test_command_2byte_parameter():
    class TransferOneParameter(Transfer):
        def __init__(self, my_param):
            self._my_param = my_param

        def pack(self) -> Optional[bytearray]:
            return self.tx_data.pack([self._my_param])

        tx = TxData(cmd_id=0xABCD, descriptor='>HH')

    tc = VerificationCommand1(tx_data=struct.pack('>H', 1))
    connection = DummyConnection(tc.tx_data)
    channel = I2cChannel(connection, crc=CrcCalculator(8, 0x31, 0xFF, 0x00))
    execute_transfer(channel, TransferOneParameter(my_param=1))


def test_command_two_2byte_parameter():
    class TransferTwoParameters(Transfer):
        def __init__(self, p1, p2):
            self._p1 = p1
            self._p2 = p2

        def pack(self) -> Optional[bytearray]:
            return self.tx_data.pack([self._p1, self._p2])

        tx = TxData(cmd_id=0xABCD, descriptor='>HHH')

    tc = VerificationCommand1(tx_data=struct.pack('>HH', 1, 2))
    connection = DummyConnection(tc.tx_data)
    channel = I2cChannel(connection, crc=CrcCalculator(8, 0x31, 0xFF, 0x00))
    execute_transfer(channel, TransferTwoParameters(p1=1, p2=2))


def test_command_two_parameter():
    class TransferTwoParameters(Transfer):
        def __init__(self, p1, p2):
            self._p1 = p1
            self._p2 = p2

        def pack(self) -> Optional[bytearray]:
            return self.tx_data.pack([self._p1, self._p2])

        tx = TxData(cmd_id=0xABCD, descriptor='>HHB')

    tc = VerificationCommand1(tx_data=struct.pack('>HB', 1, 2))
    connection = DummyConnection(tc.tx_data)
    channel = I2cChannel(connection, crc=CrcCalculator(8, 0x31, 0xFF, 0x00))
    execute_transfer(channel, TransferTwoParameters(p1=1, p2=2))


@pytest.mark.parametrize("format, input, expected", [
    ('6B', (0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff), 0xaabbccddeeff),
    ('3H', (0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff), 0xaabbccddeeff),
    ('2I', (0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff), 0x8899aabbccddeeff),
    ('4I', (0x00, 0x11, 0x22, 0x33,
            0x44, 0x55, 0x66, 0x77,
            0x88, 0x99, 0xaa, 0xbb,
            0xcc, 0xdd, 0xee, 0xff), 0x00112233445566778899aabbccddeeff)
])
def test_command_array_conversion(format, input, expected):
    class TransferWithArrayReturn(Transfer):
        def pack(self):
            return self.tx_data.pack()

        tx = TxData(cmd_id=0x01, descriptor='>H')
        rx = RxData(descriptor=f'>{format}', convert_to_int=True)

    channel = I2cChannel(I2cProgrammerMock(TestResultProvider(input)))
    result, = execute_transfer(channel, TransferWithArrayReturn())
    assert (result == expected)
