import struct

from sensirion_i2c_driver import CrcCalculator
from sensirion_i2c_driver import SensirionI2cCommand

from sensirion_i2c_adapter.command import Command, Request
from sensirion_i2c_adapter.i2c_channel import I2cChannel


class TestConnection:

    def __init__(self, expected_tx_data):
        self._expected_tx_data = expected_tx_data

    def execute(self, address, request):
        assert request.tx_data == self._expected_tx_data


class TestCommand1(SensirionI2cCommand):
    def __init__(self, command=0xABCD, tx_data=None,
                 read_delay=0.0, timeout=0, rx_length=0):
        super().__init__(command, tx_data=tx_data,
                         crc=CrcCalculator(8, 0x31, 0xFF, 0x00),
                         read_delay=0.0, timeout=0,
                         rx_length=0)


def test_command_no_additional_parameters():
    class CommandNoParameters(Command):
        requests = [Request(0xABCD, '>H')]

    tc = TestCommand1()
    connection = TestConnection(tc.tx_data)
    channel = I2cChannel(connection, crc=CrcCalculator(8, 0x31, 0xFF, 0x00))
    CommandNoParameters()(channel)


def test_command_one_byte_parameter():
    class CommandNoParameters(Command):
        requests = [Request(0xABCD, '>HB', num_params=1)]

    tc = TestCommand1(tx_data=struct.pack('B', 1))
    connection = TestConnection(tc.tx_data)
    channel = I2cChannel(connection, crc=CrcCalculator(8, 0x31, 0xFF, 0x00))
    CommandNoParameters()(channel, 1)


def test_command_2byte_parameter():
    class CommandNoParameters(Command):
        requests = [Request(0xABCD, '>HH', num_params=1)]

    tc = TestCommand1(tx_data=struct.pack('>H', 1))
    connection = TestConnection(tc.tx_data)
    channel = I2cChannel(connection, crc=CrcCalculator(8, 0x31, 0xFF, 0x00))
    CommandNoParameters()(channel, 1)


def test_command_two_2byte_parameter():
    class CommandNoParameters(Command):
        requests = [Request(0xABCD, '>HHH', num_params=2)]

    tc = TestCommand1(tx_data=struct.pack('>HH', 1, 2))
    connection = TestConnection(tc.tx_data)
    channel = I2cChannel(connection, crc=CrcCalculator(8, 0x31, 0xFF, 0x00))
    CommandNoParameters()(channel, 1, 2)


def test_command_two_parameter():
    class CommandNoParameters(Command):
        requests = [Request(0xABCD, '>HHB', num_params=2)]

    tc = TestCommand1(tx_data=struct.pack('>HB', 1, 2))
    connection = TestConnection(tc.tx_data)
    channel = I2cChannel(connection, crc=CrcCalculator(8, 0x31, 0xFF, 0x00))
    CommandNoParameters()(channel, 1, 2)
