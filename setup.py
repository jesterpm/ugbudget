#!/usr/bin/env python

from setuptools import setup, find_packages
setup(
    name="ugbudget",
    version="0.1",
    packages=find_packages(),

    install_requires=['gnucashxml >= 1.0'],

    author="Jesse Morgan",
    author_email="jesse@jesterpm.net",
    description="Usable Gnucash Budget Tools is a collection of tools to make budgeting with GnuCash simpler.",
    license="MIT",
    keywords="gnucash budget",

    entry_points={
        'console_scripts': [
            'ugbudget = ugbudget.ugbudget:main'
        ],
    }
)
