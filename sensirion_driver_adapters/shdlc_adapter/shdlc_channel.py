# -*- coding: utf-8 -*-
# (c) Copyright 2021 Sensirion AG, Switzerland

import logging
import struct
from typing import Any, Iterable, Optional, Tuple

from sensirion_shdlc_driver.errors import ShdlcDeviceError, ShdlcResponseError
from sensirion_shdlc_driver.port import ShdlcPort

from sensirion_driver_adapters.channel import TxRxChannel
from sensirion_driver_adapters.rx_tx_data import RxData

log = logging.getLogger(__name__)


class ShdlcChannel(TxRxChannel):

    def __init__(self, shdlc_port: ShdlcPort, channel_delay: float = 0.05, shdlc_address: int = 0) -> None:
        self._port = shdlc_port
        self._channel_delay = channel_delay
        self._address = shdlc_address

    def write_read(self, tx_bytes: Iterable, payload_offset: int,
                   response: RxData, device_busy_delay: float = 0.0, slave_address: Optional[int] = None,
                   ignore_errors: bool = False) -> Optional[Tuple[Any, ...]]:
        """
        Transfers the data to and from sensor.

        :param tx_bytes:
            Raw bytes to be transmitted
        :param payload_offset:
            The data my contain a header that needs to be left untouched, pushing the date through the protocol stack.
            The Payload offset points to the end of the header and the beginning of the data
        :param response:
            The response is an object that is able to unpack a raw response.
            It has to provide a method 'interpret_response.
        :param device_busy_delay:
            Indication how long the receiver of the message will be busy until processing of the data has been
            completed.
        :param slave_address:
            Used for shdlc address
        :param ignore_errors:
            Some transfers may generate an exception even when they execute properly. In these situations the exception
            is swallowed and an empty result is returned
        :return:
            Return a tuple of the interpreted data or None if there is no response at all
        """
        shdlc_address = slave_address or self._address
        cmd_id = struct.unpack('>B', tx_bytes[0:payload_offset])[0]
        data = tx_bytes[payload_offset:]
        timeout = max(self._channel_delay, device_busy_delay)
        rx_addr, rx_cmd, rx_state, rx_data = self._port.transceive(slave_address=shdlc_address,
                                                                   command_id=cmd_id,
                                                                   data=data,
                                                                   response_timeout=timeout)
        if rx_addr != shdlc_address:
            raise ShdlcResponseError("Received slave address {} instead of {}."
                                     .format(rx_addr, shdlc_address))
        if rx_cmd != cmd_id:
            raise ShdlcResponseError("Received command ID 0x{:02X} instead of "
                                     "0x{:02X}.".format(rx_cmd, cmd_id))
        error_state = True if rx_state & 0x80 else False
        if error_state:
            log.warning("SHDLC device with address {} is in error state."
                        .format(shdlc_address))
        error_code = rx_state & 0x7F
        if error_code:
            log.warning("SHDLC device with address {} returned error {}."
                        .format(shdlc_address, error_code))
            raise ShdlcDeviceError(error_code)  # Command failed to execute
        if response:
            # The size of strings (and arrays?) is not known before receiving the response. The indications
            # in the rx descriptor are only the upper bounds. Therefore, each field is unpacked individually
            # and the position in the result frame is computed online.
            return response.unpack_dynamic_sized(rx_data)

    def strip_protocol(self, data) -> None:
        """The protocol is already stripped by the connection"""
        return data

    @property
    def timeout(self) -> float:
        return self._channel_delay
