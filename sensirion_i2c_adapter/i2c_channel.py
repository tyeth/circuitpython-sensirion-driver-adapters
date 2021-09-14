# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from sensirion_i2c_driver import I2cConnection
from sensirion_i2c_driver.errors import I2cChecksumError
from .channel import TxRxChannel, TxRxRequest


class I2cChannel(TxRxChannel):

    def __init__(self, connection: I2cConnection, slave_address, crc):
        self._connection = connection
        self._slave_address = slave_address
        self._crc = crc

    def write_read(self, tx_data, payload_offset, response, device_busy_delay=0.0, slave_address=None):
        tx_data = I2cChannel._build_tx_data(tx_data, payload_offset, self._crc)
        rx_len = 0
        if response:
            rx_len = 3 * response.rx_length // 2
        tx_rx = TxRxRequest(channel=self, response=response, tx_data=tx_data, device_busy_delay=device_busy_delay,
                            receive_length=rx_len)
        if slave_address is None:
            slave_address = self._slave_address
        return self._connection.execute(slave_address, tx_rx)

    def strip_protocol(self, data):
        """
        Validates the CRCs of the received data from the device and returns
        the data with all CRCs removed.

        :param bytes data:
            Received raw bytes from the read operation.
        :return:
            The received bytes without crc, or None if there is no data received.
        :rtype:
            bytes or None
        :raise ~sensirion_i2c_driver.errors.I2cChecksumError:
            If a received CRC was wrong.
        """
        if self._crc is None:
            return data  # data does not contain CRCs -> return it as-is

        data = bytearray(data)  # Python 2 compatibility
        data_without_crc = bytearray()
        for i in range(len(data)):
            if i % 3 == 2:
                received_crc = data[i]
                expected_crc = self._crc(data[i - 2:i])
                if received_crc != expected_crc:
                    raise I2cChecksumError(received_crc, expected_crc, data)
            else:
                data_without_crc.append(data[i])
        return bytes(data_without_crc) if len(data_without_crc) else None

    @staticmethod
    def _build_tx_data(tx_data, cmd_width, crc):
        """
        Build the raw bytes to send from given command and TX data.

        :param cmd_width: See
            :py:meth:`~sensirion_i2c_driver.sensirion_command.SensirionI2cCommand.__init__`.
        :param tx_data: See
            :py:meth:`~sensirion_i2c_driver.sensirion_command.SensirionI2cCommand.__init__`.
        :param crc: See
            :py:meth:`~sensirion_i2c_driver.sensirion_command.SensirionI2cCommand.__init__`.
        :return:
            The raw bytes to send, or None if no write header is needed.
        :rtype:
            bytearray/None
        """
        if not tx_data:
            return None

        data = bytearray(tx_data[:cmd_width]) # the command is in the beginning of the tx_data
        tx_data = bytearray(tx_data[cmd_width:] or [])  # Python 2 compatibility
        for i in range(len(tx_data)):
            data.append(tx_data[i])
            if (crc is not None) and (i % 2 == 1):
                data.append(crc(tx_data[i - 1:i + 1]))
        return bytes(data)
