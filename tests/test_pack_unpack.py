# -*- coding: utf-8 -*-
# (c) Copyright 2022 Sensirion AG, Switzerland

import struct
from typing import Iterable

import pytest

from sensirion_driver_adapters.rx_tx_data import RxData, TxData


@pytest.mark.parametrize("tx, data", [
    (TxData(0xABCD, ">HH"), (1234,)),
    (TxData(0xABCD, ">HH8B"), (1234, [0] * 8))]
                         )
def test_pack(tx: TxData, data):
    packed = tx.pack(data)
    ref = [tx._cmd_id]
    for d in data:
        if isinstance(d, Iterable):
            ref.extend(d)
        else:
            ref.append(d)
    unpacked = list(struct.unpack(tx._descriptor, packed))
    not_equal = filter(lambda x: x[0] != x[1], zip(ref, unpacked))
    assert not any(not_equal)


@pytest.mark.parametrize("rx, data", [(RxData(">HH"), (0xABCD, 1234,))])
def test_unpack(rx: RxData, data):
    packed = struct.pack(rx._descriptor, *data)
    unpacked = rx.unpack(packed)
    not_equal = filter(lambda x: x[0] != x[1], zip(data, unpacked))
    assert not any(not_equal)


@pytest.mark.parametrize("rx, data", [(RxData(">HH"), (0xABCD, 1234)),
                                      (RxData(">HH8B"), (0xABCD, 1234, 1, 2, 3, 4, 5, 6, 7, 8))])
def test_dynamic_unpack(rx: RxData, data):
    packed = struct.pack(rx._descriptor, *data)
    unpacked = rx.unpack_dynamic_sized(packed)
    not_equal = filter(lambda x: x[0] != x[1], zip(data, unpacked))
    assert not any(not_equal)
