# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function

from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection
from sensirion_shdlc_sensorbridge import SensorBridgePort, \
    SensorBridgeShdlcDevice, SensorBridgeI2cProxy

from sensirion_i2c_adapter.command import Command, Request, Response
from sensirion_i2c_adapter.i2c_channel import I2cChannel
from sensirion_i2c_driver import I2cConnection, CrcCalculator


class StartMeasurement(Command):
    requests = [Request(0x21, ">H", device_busy_delay=2.0)]


class StopMeasurements(Command):
    requests = [Request(0x104, '>H', device_busy_delay=1.0)]


class ReadResults(Command):
    requests = [Request(0x3C4, descriptor='>H', device_busy_delay=0.01)]
    responses = [Response(descriptor='>HHHHHHHH')]


def test_command_invocation():

    with ShdlcSerialPort(port='/dev/ttyUSB2', baudrate=460800) as port:
        bridge = SensorBridgeShdlcDevice(ShdlcConnection(port), slave_address=0)
        print("SensorBridge SN: {}".format(bridge.get_serial_number()))

        # Configure SensorBridge port 1 for SPS6x
        bridge.set_i2c_frequency(SensorBridgePort.ONE, frequency=100e3)
        bridge.set_supply_voltage(SensorBridgePort.ONE, voltage=5.0)
        bridge.switch_supply_on(SensorBridgePort.ONE)

        i2c_transceiver = SensorBridgeI2cProxy(bridge, port=SensorBridgePort.ONE)
        channel = I2cChannel(I2cConnection(i2c_transceiver), slave_address=0x69, crc=CrcCalculator(8, 0x31, 0xFF, 0x00))

        StartMeasurement(channel)()

        for i in range(100):
            res = ReadResults(channel)()
            print(res)

        StopMeasurements(channel)()



test_command_invocation()