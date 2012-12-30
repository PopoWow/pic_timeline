#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2012-2013 Kyle Kawamura
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from Tkinter import N, S, W, E
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------        

# appdirs
DEVELOPER_NAME = "kylekawa"

# Tkinter
HEIGHT = N+S
WIDTH = W+E
ALL = HEIGHT+WIDTH

# logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LEVELS = {'debug'   : DEBUG,
          'info'    : INFO,
          'warning' : WARNING,
          'error'   : ERROR,
          'critical': CRITICAL
         }

# DateTimeDialog
CLEAR_OVERRIDE = "clear"
