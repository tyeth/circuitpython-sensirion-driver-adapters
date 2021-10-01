# -*- coding: utf-8 -*-
# (c) Copyright 2021 Sensirion AG, Switzerland
import struct
from typing import Optional

from sensirion_i2c_adapter.i2c_channel import I2cChannel
from sensirion_i2c_adapter.transfer import Transfer, TxData, execute_transfer
from sensirion_i2c_driver import CrcCalculator
from sensirion_i2c_driver import SensirionI2cCommand


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
