# -*- coding: utf-8 -*-
# (c) Copyright 2022 Sensirion AG, Switzerland

import pytest
from sensirion_shdlc_driver import ShdlcSerialPort
from sensirion_shdlc_driver.errors import ShdlcDeviceError

from sensirion_driver_adapters.shdlc_adapter.shdlc_channel import ShdlcChannel
from sensirion_driver_adapters.transfer import execute_transfer, Transfer, TxData, RxData


class ProductType(Transfer):
    CMD_ID = 0xD0

    def pack(self):
        return self.tx_data.pack([0])

    tx = TxData(CMD_ID, '>BB', device_busy_delay=0.05, slave_address=None, ignore_ack=False)
    rx = RxData('>32s')


class ProductName(Transfer):
    CMD_ID = 0xd0

    def pack(self):
        return self.tx_data.pack([1])

    tx = TxData(CMD_ID, '>BB', device_busy_delay=0.05, slave_address=None, ignore_ack=False)
    rx = RxData('>32s')


class FirmwareVersion(Transfer):
    CMD_ID = 0xd1

    def pack(self):
        return self.tx_data.pack([])

    tx = TxData(CMD_ID, '>B', device_busy_delay=0.05, slave_address=None, ignore_ack=False)
    rx = RxData('>BB?BBBB')


class StartMeasurement(Transfer):
    CMD_ID = 0x0

    def pack(self):
        return self.tx_data.pack([0])

    tx = TxData(CMD_ID, '>BB', device_busy_delay=0.05, slave_address=None, ignore_ack=False)


class StopMeasurement(Transfer):
    CMD_ID = 0x1

    def pack(self):
        return self.tx_data.pack([])

    tx = TxData(CMD_ID, '>B', device_busy_delay=0.05, slave_address=None, ignore_ack=False)


class GetVocState(Transfer):
    CMD_ID = 0x61

    def pack(self):
        return self.tx_data.pack([8])

    tx = TxData(CMD_ID, '>BB', device_busy_delay=0.05, slave_address=None, ignore_ack=False)
    rx = RxData('>32B')


class MiniSvm41:

    def __init__(self, channel):
        self._channel = channel

    def get_product_type(self):
        return execute_transfer(self._channel, ProductType())[0]

    def get_product_name(self):
        return execute_transfer(self._channel, ProductName())[0]

    def get_firmware_version(self):
        return execute_transfer(self._channel, FirmwareVersion())

    def start_measurement(self):
        execute_transfer(self._channel, StartMeasurement())

    def stop_measurement(self):
        execute_transfer(self._channel, StopMeasurement())

    def get_voc_state(self):
        return execute_transfer(self._channel, GetVocState())


@pytest.fixture
def svm41():
    with ShdlcSerialPort('COM9', baudrate=115200) as port:
        channel = ShdlcChannel(port, 0.1)
        sensor = MiniSvm41(channel)
        yield sensor


@pytest.mark.needs_hardware
def test_get_product_type(svm41):
    p_type = svm41.get_product_type()
    assert p_type == b'00141000'


@pytest.mark.needs_hardware
def test_get_product_name(svm41):
    p_name = svm41.get_product_name()
    assert p_name == b'SVM41'


@pytest.mark.needs_hardware
def test_get_firmware_version(svm41):
    version = svm41.get_firmware_version()
    assert len(version) == 7


@pytest.mark.needs_hardware
def test_get_voc_state(svm41):
    try:
        svm41.start_measurement()
    except BaseException:
        pass
    try:
        voc_state = svm41.get_voc_state()
        assert len(voc_state) == 8
    finally:
        try:
            svm41.stop_measurement()
        except ShdlcDeviceError:
            pass
