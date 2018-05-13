#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages


setup(
    name='wazo-ctid-queue',
    version='0.0.1',
    description='Wazo CTI queue',
    author='Sylvain Boily',
    author_email='sylvain@wazo.io',
    url='http://www.wazo.io/',
    license='GPLv3',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'wazo_ctid_queue': ['api.yml'],
    },
    entry_points={
        'xivo_ctid_ng.plugins': [
            'queue = wazo_ctid_queue.plugin:Plugin'
        ],
    },
)
