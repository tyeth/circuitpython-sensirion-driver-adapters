# -*- coding: utf-8 -*-
# (c) Copyright 2021 Sensirion AG, Switzerland
from __future__ import absolute_import, division, print_function

import abc

from .channel import TxRxChannel


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
