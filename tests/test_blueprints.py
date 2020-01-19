# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from __future__ import absolute_import, print_function

import pytest
from flask import Flask

from oarepo_fsm import OARepoFSM
from oarepo_fsm.ext import _OARepoFSMState
from oarepo_fsm.proxies import current_oarepo_fsm


def test_init(app):
    """Test blueprint initialization."""
    assert 'oarepo_fsm' in app.blueprints

def test_fsm_blueprint(app):
    """Test dynamic /fsm url rules."""
    assert 'records' in current_oarepo_fsm.fsm_endpoints
