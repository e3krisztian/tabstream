# coding: utf-8

from setuptools import setup

import sys
PY2 = sys.version_info[0] < 3
PY3 = not PY2


PY2_UNICODECSV = ['unicodecsv'] if PY2 else []


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
    install_requires=PY2_UNICODECSV,
    dependency_links=[
        ('https://github.com/krisztianfekete/externals/tarball/master'
         '#egg=externals-0.0dev')],

    use_2to3=PY3,
    use_2to3_fixers=['custom_2to3_fixers'],
    )
