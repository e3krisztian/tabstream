# coding: utf-8

from setuptools import setup


import sys
PY2 = sys.version_info[0] < 3
PY3 = not PY2


setup(
    name='csvx',
    version='0.1.0',
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

    py_modules=['csvx', 'test_csvx'],
    test_suite='test_csvx',

    install_requires=['unicodecsv'] if PY2 else [],
    use_2to3=PY3,
    use_2to3_fixers=['custom_2to3_fixers'],
    )
