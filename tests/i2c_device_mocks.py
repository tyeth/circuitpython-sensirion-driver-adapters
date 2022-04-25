# -*- coding: utf-8 -*-
# (c) Copyright 2021 Sensirion AG, Switzerland
import logging
import random
import struct
import time
from typing import Optional, Tuple, Any

from sensirion_i2c_driver.crc_calculator import CrcCalculator

from sensirion_i2c_adapter.channel import TxRxChannel, TxRxRequest, AbstractMultiChannel
from sensirion_i2c_adapter.i2c_channel import I2cChannel
from sensirion_i2c_adapter.multi_channel import MultiChannel
from sensirion_i2c_adapter.transfer import Transfer, TxData, RxData, execute_transfer

device_logger = logging.getLogger('device_logger')
device_logger.setLevel(logging.INFO)


class I2cSensorMock:
    def __init__(self, id: int, i2c_address: int, crc: CrcCalculator, cmd_width: int = 2) -> None:
        self._id = id
        self._i2c_address = i2c_address
        self._cmd_width = cmd_width
        self._cmd_template = '>H' if cmd_width == 2 else 'B'
        self._crc = crc

    def write(self, address: int, data: bytes) -> None:
        assert address == self._i2c_address, "unsupported i2c address"
        cmd = struct.unpack(self._cmd_template, data[:self._cmd_width])
        device_logger.info(f'device {self._id} received commands {cmd}')

    def read(self, address, nr_of_bytes_to_return) -> bytes:
        nr_of_bytes = 2 * nr_of_bytes_to_return // 3
        assert address == self._i2c_address, "unsupported i2c address"
        device_logger.info(f'device {self._id} received read request for {nr_of_bytes} bytes')
        rx_data = [random.randint(0, 255) for i in range(nr_of_bytes)]
        data = bytearray()
        for i in range(len(rx_data)):
            data.append(rx_data[i])
            if (self._crc is not None) and (i % 2 == 1):
                data.append(self._crc(rx_data[i - 1:i + 1]))
        return data


class I2cProgrammerMock:

    def __init__(self, device_mock) -> None:
        self._connected_device = device_mock

    def execute(self, address: int, tx_rx: TxRxRequest) -> Optional[Tuple[Any]]:
        if tx_rx.tx_data is not None:
            self._connected_device.write(address, tx_rx.tx_data)
            if tx_rx.read_delay > 0:
                time.sleep(tx_rx.read_delay)
        if tx_rx.rx_length > 0:
            data = self._connected_device.read(address, tx_rx.rx_length)
            return tx_rx.interpret_response(data)
        return None


class MeasureRawSignals(Transfer):
    CMD_ID = 0x2619

    def __init__(self, relative_humidity, temperature):
        self._relative_humidity = relative_humidity
        self._temperature = temperature

    def pack(self):
        return self.tx_data.pack([self._relative_humidity, self._temperature])

    tx = TxData(CMD_ID, '>HHH', device_busy_delay=0.05, slave_address=None, ignore_ack=False)
    rx = RxData('>HH')


class DummyDriver:

    def __init__(self, channel) -> None:
        self._channel = channel

    def invoke_command(self, hum, temp) -> Any:
        t = MeasureRawSignals(hum, temp)
        return execute_transfer(self.channel, t)

    @property
    def channel(self) -> TxRxChannel:
        return self._channel


def create_multi_channel(nr_of_channels: int, i2c_address: int,
                         cmd_width: int,
                         crc: CrcCalculator) -> AbstractMultiChannel:
    channels = tuple([I2cChannel(I2cProgrammerMock(I2cSensorMock(i, i2c_address, crc, cmd_width)),
                                 i2c_address, crc) for i in range(nr_of_channels)])
    return MultiChannel(channels)
