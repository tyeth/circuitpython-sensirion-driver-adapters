# -*- coding: utf-8 -*-
# (c) Copyright 2023 Sensirion AG, Switzerland


def pytest_addoption(parser):
    """
    Register command line options
    """
    parser.addoption("--serial-port", action="store", type=str)
