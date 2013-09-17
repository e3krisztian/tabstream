# coding: utf-8

from setuptools import setup

import sys
PY3 = sys.version_info.major == 3


setup(
    name='csvx',
    version=':versiontools:csvx:',
    description='CSV eXtensions - easy reading of CSV streams with header',
    author='Krisztián Fekete',
    author_email='fekete.krisztyan@gmail.com',

    license='MIT License',

    classifiers=[
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        ],

    packages=['csvx'],

    setup_requires=['versiontools >= 1.8'],

    use_2to3=PY3,
    )
