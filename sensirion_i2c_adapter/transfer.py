# -*- coding: utf-8 -*-
# (c) Copyright 2021 Sensirion AG, Switzerland
from __future__ import absolute_import, division, print_function

import abc
import struct

from .channel import TxRxChannel


class TxData:
    """Models the tx data that is exchanged. It it primarily a descriptor that knows how to convert structured
    data into a list of raw bytes"""

    def __init__(self, cmd_id,
                 descriptor,
                 device_busy_delay=0.0,
                 slave_address=None,
                 ignore_ack=False):
        self._cmd_id = cmd_id
        self._command_width = 2
        if descriptor.startswith('>B'):
            self._command_width = 1
        self._descriptor = descriptor
        self._slave_address = slave_address
        self._device_busy_delay = device_busy_delay
        self._ignore_acknowledge = ignore_ack

    def pack(self, argument_list=[]):
        data_to_pack = tuple([self._cmd_id] + argument_list)
        return bytearray(struct.pack(self._descriptor, *data_to_pack))

    @property
    def command_width(self):
        return self._command_width

    @property
    def slave_address(self):
        return self._slave_address

    @property
    def device_busy_delay(self):
        return self._device_busy_delay

    @property
    def ignore_acknowledge(self):
        return self._ignore_acknowledge


class RxData:
    """Descriptor for data to be received"""
    def __init__(self, descriptor=None):
        self._descriptor = descriptor
        self._rx_length = 0
        if self._descriptor is not None:
            self._rx_length = struct.calcsize(self._descriptor)

    @property
    def rx_length(self):
        return self._rx_length

    def unpack(self, data):
        return struct.unpack(self._descriptor, data)


class Transfer(abc.ABC):
    """A transfer abstracts the data that is exchanged between host and sensor"""

    @property
    def ignore_error(self):
        tx = self.tx_data
        if tx is not None:
            return tx.ignore_acknowledge
        return False

    @abc.abstractmethod
    def pack(self):
        raise NotImplementedError()

    @property
    def command_width(self):
        tx = self.tx_data
        if tx is None:
            return 0
        return self.tx_data.command_width

    @property
    def device_busy_delay(self):
        tx = self.tx_data
        if tx is None:
            return 0
        return tx.device_busy_delay

    @property
    def slave_address(self):
        tx = self.tx_data
        if tx is None:
            return None
        return self.tx_data.slave_address

    @property
    def tx_data(self):
        if not hasattr(self.__class__, 'tx'):
            return None
        return getattr(self.__class__, 'tx')

    @property
    def rx_data(self):
        if not hasattr(self.__class__, 'rx'):
            return None
        return getattr(self.__class__, 'rx')


def execute_transfer(channel: TxRxChannel, *args):
    """
    Executes a transfer consisting of one or more Transfer objects.
    :param channel: The channel that is used to transfer the data
    :param args: a variable list of transfers to be transmitted
    :return: a tuple of data if the last transfer has a response
    """
    transfers = list(args)
    for t in transfers[:-1]:
        channel.write_read(t.pack(), t.command_width,
                           t.rx_data, device_busy_delay=t.device_busy_delay,
                           slave_address=t.slave_address, ignore_errors=t.ignore_error)
    t = transfers[-1]
    return channel.write_read(t.pack(), t.command_width,
                              t.rx_data, device_busy_delay=t.device_busy_delay,
                              slave_address=t.slave_address, ignore_errors=t.ignore_error)
