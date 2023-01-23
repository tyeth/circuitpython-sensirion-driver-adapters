# -*- coding: utf-8 -*-
# (c) Copyright 2023 Sensirion AG, Switzerland
import time

import pytest
from sensirion_shdlc_sensorbridge import (SensorBridgePort)

from sensirion_driver_adapters.i2c_adapter.i2c_channel import I2cChannel
from sensirion_driver_adapters.i2c_adapter.sensor_bridge_i2c_channel_provider import SensorBridgeI2cChannelProvider


@pytest.mark.needs_hardware
def test_invoke_general_call_reset_with_hw():
    """Issue a general call reset using the sensor bridge

    The sensor bridge reports an error when sending command 6 to slave address 0.
    """

    channel_provider = SensorBridgeI2cChannelProvider(SensorBridgePort.ONE, "COM12", serial_baud_rate=460800)
    channel_provider.supply_voltage = 5.0
    channel_provider.i2c_frequency = 50e3
    with channel_provider:
        # test with scd3x to check if reset becomes active
        channel = channel_provider.get_channel(0x61, (8, 0x31, 0xFF, 0x00))
        time.sleep(1)
        assert isinstance(channel, I2cChannel)
        channel.i2c_general_call_reset()
