# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions"""

from __future__ import absolute_import, print_function
from . import config


class _OARepoFSMState(object):
    """oarepo-fsm state object."""

    def __init__(self, app):
        """Initialize state."""
        self.app = app


class OARepoFSM(object):
    """oarepo-fsm extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions['oarepo-fsm'] = _OARepoFSMState(app)

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith('OAREPO_FSM'):
                app.config.setdefault(k, getattr(config, k))
