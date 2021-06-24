#!/usr/bin/env python

from distutils.core import setup

from erlterm import __version__ as version

setup(
    name = 'erlterm',
    version = version,
    description = 'ErlTerm',
    author = 'fycheung',
    author_email = 'fycheung@163.com',
    url = 'http://github.com/samuel/python-erlterm',
    packages = ['erlterm'],
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
