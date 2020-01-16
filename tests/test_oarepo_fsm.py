# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from __future__ import absolute_import, print_function

from flask import Flask

from oarepo_fsm import OARepoFSM


def test_version():
    """Test version import."""
    from oarepo_fsm import __version__
    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask('testapp')
    ext = OARepoFSM(app)
    assert 'oarepo-fsm' in app.extensions

    app = Flask('testapp')
    ext = OARepoFSM()
    assert 'oarepo-fsm' not in app.extensions
    ext.init_app(app)
    assert 'oarepo-fsm' in app.extensions
