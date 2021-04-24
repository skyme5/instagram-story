#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .instagram import Instagram
from .main import main

# if somebody does "from somepackage import *", this is what they will
# be able to access:
__all__ = [
    "Instagram",
    "main",
]
