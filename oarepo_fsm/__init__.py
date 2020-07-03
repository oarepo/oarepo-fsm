# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions."""

from __future__ import absolute_import, print_function

from .ext import OARepoFSM
from .version import __version__

__all__ = ('__version__', 'OARepoFSM')
