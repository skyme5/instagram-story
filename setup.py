#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools
with open('README.md', 'r') as fh:
    long_description = fh.read()

version = {}
with open("instagram/version.py") as fp:
    exec(fp.read(), version)

setuptools.setup(
    name='instagram-story',
    version=version['__version__'],
    author='Aakash Gajjar',
    author_email='skyme5@gmx.com',
    description='Instagram Story downloader',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/skyme5/instagram-story',
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['instagram-story=instagram.main:main'],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    keywords='instagram story',
)
