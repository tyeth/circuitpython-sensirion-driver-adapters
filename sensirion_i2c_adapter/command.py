# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland
import abc
import struct
from typing import List

from .channel import TxRxChannel


class Request:

    def __init__(self, cmd_id, descriptor, num_params=0, device_busy_delay=0.0, slave_address=None):
        self._cmd_id = cmd_id
        self._command_width = 2
        if descriptor.startswith('>B'):
            self._command_width = 1
        self._num_params = num_params
        self._descriptor = descriptor
        self._slave_address = slave_address
        self._device_busy_delay = device_busy_delay

    def pack(self, argument_list, offset):
        data_to_pack = tuple([self._cmd_id] + argument_list[offset: offset + self._num_params])
        offset += self._num_params
        return offset, bytearray(struct.pack(self._descriptor, *data_to_pack))

    @property
    def command_width(self):
        return self._command_width

    @property
    def slave_address(self):
        return self._slave_address

    @property
    def device_busy_delay(self):
        return self._device_busy_delay


class Response:

    def __init__(self, descriptor=None):
        self._descriptor = descriptor
        self._rx_length = 0
        if self._descriptor is not None:
            self._rx_length = struct.calcsize(self._descriptor)

    @property
    def rx_length(self):
        return self._rx_length

    def unpack(self, data):
        # buffer = bytearray(struct.calcsize(self._descriptor))
        return struct.unpack(self._descriptor, data)


class Command(abc.ABC):

    def __call__(self, channel: TxRxChannel, *args, **kwargs):
        argument_offset = 0
        argument_list = list(args)
        for request in self.req[:-1]:
            argument_offset, data = request.pack(argument_list, argument_offset)
            channel.write_read(data, request.command_width,
                               None, device_busy_delay=request.device_busy_delay,
                               slave_address=request.slave_address)
        response = None
        request = self.req[-1]
        response = self.resp[-1] if len(self.resp) > 0 else None
        argument_offset, data = request.pack(argument_list, argument_offset)
        return channel.write_read(data, request.command_width,
                                  response, device_busy_delay=request.device_busy_delay,
                                  slave_address=request.slave_address)

    @property
    def req(self) -> List[Request]:
        if not hasattr(self.__class__, 'requests'):
            return []
        return getattr(self.__class__, 'requests')

    @property
    def resp(self) -> List[Request]:
        if not hasattr(self.__class__, 'responses'):
            return []
        return getattr(self.__class__, 'responses')
