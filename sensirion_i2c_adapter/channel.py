# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland
import abc


class TxRxChannel(abc.ABC):

    @abc.abstractmethod
    def write_read(self, tx_data, payload_offset, response, device_busy_delay=0.0, slave_address=None):
        pass

    @abc.abstractmethod
    def strip_protocol(self, data):
        pass


class TxRxRequest:

    def __init__(self, channel, tx_data=None, response=None, device_busy_delay=0.0):
        self._channel: TxRxChannel = channel
        self._response = response
        self._tx_data = tx_data
        self._device_busy_delay = device_busy_delay

    @property
    def read_delay(self):
        return self._device_busy_delay

    @property
    def tx_data(self):
        return self._tx_data

    @property
    def rx_length(self):
        return 0 if self._response is None else self._response.rx_length

    @property
    def timeout(self):
        if self._response is not None:
            return 0.0
        return self._device_busy_delay

    @property
    def post_processing_time(self):
        return self.timeout

    def interpret_response(self, data):
        raw_data = self._channel.strip_protocol(data)
        if self._response is not None:
            return self._response.unpack(raw_data)
        return None
