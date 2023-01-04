# -*- coding: utf-8 -*-
# (c) Copyright 2023 Sensirion AG, Switzerland

import abc


class ResponseProvider(abc.ABC):
    """Abstract base class that allows to inject arbitrary responses into a sensor mock.
    """

    @abc.abstractmethod
    def get_id(self) -> str:
        """Return an identifier of the response provider"""

    @abc.abstractmethod
    def handle_command(self, cmd_id: int, data: bytes, response_length: int) -> bytes:
        """
        Provide a hook for sensor specific command handling.

        With specific implementation of this class, it becomes possible to emulate any sensor.

        :param cmd_id:
            Command id of the command to emulate
        :param data:
            The parameters of the command. At this point the data do not contain a crc anymore
        :param response_length:
            The expected length of the returned bytes array

        :return:
            An emulated response.
        """
