#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages


setup(
    name='wazo-calld-queue',
    version='0.0.1',
    description='Wazo calld queue',
    author='Sylvain Boily',
    author_email='sylvain@wazo.io',
    url='http://www.wazo.io/',
    license='GPLv3',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'wazo_call_queue': ['api.yml'],
    },
    entry_points={
        'wazo_calld.plugins': [
            'queue = wazo_calld_queue.plugin:Plugin'
        ],
    },
)
