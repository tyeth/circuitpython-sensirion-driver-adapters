# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from setuptools import setup, find_packages
import os
import re


# Read version number from version.py
version_line = open("sensirion_i2c_driver/version.py", "rt").read()
result = re.search(r"^version = ['\"]([^'\"]*)['\"]", version_line, re.M)
if result:
    version_string = result.group(1)
else:
    raise RuntimeError("Unable to find version string")


# Use README.rst and CHANGELOG.rst as package description
root_path = os.path.dirname(__file__)
readme = open(os.path.join(root_path, 'README.rst')).read()
changelog = open(os.path.join(root_path, 'CHANGELOG.rst')).read()
long_description = readme.strip() + "\n\n" + changelog.strip() + "\n"


setup(
    name='sensirion_i2c_adapters',
    version=version_string,
    author='Rolf Laich',
    author_email='rolf.laich@sensirion.com',
    description='Adapter classes to be used by MSO-SW driver generator',
    license='BSD',
    keywords='sensirion driver adapters',
    url='https://gitlab.sensirion.lokal/MSO-SW/drivers/python-driver-adapters',
    packages=find_packages(exclude=['tests', 'tests.*']),
    long_description=long_description,
    python_requires='=3.8.*, <4',
    install_requires=[
    ],
    extras_require={
        'test': [
            'flake8~=3.6.0',
            'mock~=3.0.0',
            'pytest~=3.10.0',
            'pytest-cov~=2.6.0',
        ]
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.8',
        'Topic :: System :: Hardware :: Hardware Drivers :: Driver Generator'
    ]
)
