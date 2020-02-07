# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# examples is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from __future__ import absolute_import, print_function


def test_version():
    """Test version import."""
    from oarepo_fsm import __version__
    assert __version__


def test_init():
    # """Test extension initialization."""
    pass
    # app = Flask('testapp')
    # ext = OARepoFSM(app)
    # assert 'oarepo-fsm' in app.extensions
    #
    # app = Flask('testapp')
    # ext = OARepoFSM()
    # assert 'oarepo-fsm' not in app.extensions
    # ext.init_app(app)
    # assert 'oarepo-fsm' in app.extensions


def test_state():
    """Test extension state initialization."""
    pass
    # app = Flask('testapp')
    # ext = OARepoFSM(app)
    # ext.init_app(app)
    #
    # state = app.extensions['oarepo-fsm']
    #
    # assert isinstance(state, _OARepoFSMState)


# def test_alembic(app, db):
#     """Test alembic recipes."""
    # ext = app.extensions['invenio-db']
    #
    # if db.engine.name == 'sqlite':
    #     raise pytest.skip('Upgrades are not supported on SQLite.')
    #
    # assert not ext.alembic.compare_metadata()
    # db.drop_all()
    # ext.alembic.upgrade()
    #
    # assert not ext.alembic.compare_metadata()
