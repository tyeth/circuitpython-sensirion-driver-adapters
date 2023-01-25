# -*- coding: utf-8 -*-
# (c) Copyright 2022 Sensirion AG, Switzerland

import pytest
from sensirion_shdlc_driver.errors import ShdlcDeviceError

from sensirion_driver_adapters.mocks.mock_shdlc_channel_provider import ShdlcMockPortChannelProvider
from sensirion_driver_adapters.mocks.response_provider import ResponseProvider, random_bytes
from sensirion_driver_adapters.rx_tx_data import RxData, TxData
from sensirion_driver_adapters.shdlc_adapter.shdlc_serial_channel_provider import ShdlcSerialPortChannelProvider
from sensirion_driver_adapters.transfer import execute_transfer, Transfer


class Svm41ResponseProvider(ResponseProvider):
    CMD_TABLE = {0xd0: {0: '00141000'.encode("ascii"),
                        1: 'SVM41'.encode("ascii")}
                 }

    def get_id(self) -> str:
        return "svm42-response"

    def handle_command(self, cmd_id: int, data: bytes, response_length: int) -> bytes:
        if cmd_id not in self.CMD_TABLE:
            return random_bytes(response_length)
        cmd_id_entry = self.CMD_TABLE[cmd_id]
        if isinstance(cmd_id_entry, dict):
            assert len(data) > 0, "No subcommand specified"
            subcommand = data[0]
            if subcommand not in cmd_id_entry:
                return random_bytes(response_length)
            cmd_id_entry = cmd_id_entry[subcommand]
        if isinstance(cmd_id_entry, bytes):
            return cmd_id_entry
        if callable(cmd_id_entry):
            return cmd_id_entry(response_length)
        raise AssertionError("Invalid response handler")


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
    rx = RxData('>8B')


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
        return execute_transfer(self._channel, GetVocState())[0]


@pytest.fixture
def channel_provider(request):
    port = request.config.getoption("--serial-port")
    if port is not None:
        provider = ShdlcSerialPortChannelProvider(serial_port=port, serial_baud_rate=115200)
        return provider
    return ShdlcMockPortChannelProvider(response_provider=Svm41ResponseProvider())


@pytest.fixture
def svm41(channel_provider):
    with channel_provider:
        channel = channel_provider.get_channel(0.1)
        sensor = MiniSvm41(channel)
        yield sensor


def test_get_product_type(svm41):
    p_type = svm41.get_product_type()
    assert p_type == '00141000'


def test_get_product_name(svm41):
    p_name = svm41.get_product_name()
    assert p_name == 'SVM41'


def test_get_firmware_version(svm41):
    version = svm41.get_firmware_version()
    assert len(version) == 7


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
