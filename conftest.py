#!/usr/bin/env python
# -*- coding: utf-8 -*-


def pytest_addoption(parser):
    """
    Set configuration values programmatically. The settings with a % in the default may not be set in
    the configuration file since it will be interpreted as interpolation value by distutils
    this is a known bug..
    """
    parser.addini(name="log_cli", help="Flag to enable/disable logging", default=True)
    parser.addini(name="log_cli_level", help="Log level", default='INFO')
    parser.addini(name="log_cli_format", help="format of log entries",
                  default="%(asctime)s.%(msecs)03d [%(levelname)6s] %(message)s")
    parser.addini(name="log_cli_date_format", help="data format of asctime", default="%H:%M:%S")
