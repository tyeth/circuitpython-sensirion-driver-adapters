# -*- coding: utf-8 -*-
# (c) Copyright 2021 Sensirion AG, Switzerland
from typing import Any

from sensirion_i2c_driver.crc_calculator import CrcCalculator

from sensirion_driver_adapters.channel import TxRxChannel, AbstractMultiChannel
from sensirion_driver_adapters.i2c_adapter.i2c_channel import I2cChannel
from sensirion_driver_adapters.mocks.i2c_connection_mock import I2cConnectionMock
from sensirion_driver_adapters.mocks.i2c_sensor_mock import I2cSensorMock
from sensirion_driver_adapters.multi_channel import MultiChannel
from sensirion_driver_adapters.rx_tx_data import TxData, RxData
from sensirion_driver_adapters.transfer import Transfer, execute_transfer


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
    channels = tuple([I2cChannel(I2cConnectionMock(I2cSensorMock(i2c_address, crc, cmd_width, i)),
                                 i2c_address, crc) for i in range(nr_of_channels)])
    return MultiChannel(channels)
