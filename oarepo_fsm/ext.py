# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions"""

from __future__ import absolute_import, print_function

from flask import Blueprint
from invenio_base.signals import app_loaded

from . import config
from .mixins import StatefulRecordMixin
from .views import StatefulRecordActions


class _OARepoFSMState(object):
    """oarepo-fsm state object."""

    def __init__(self, app):
        """Initialize state."""
        self.app = app
        self.schema_map = {}

    def app_loaded(self, app):
        with app.app_context():
            self._register_blueprints(app)
            self._connect_model_callbacks(app)
            self._connect_index_callbacks(app)

    def _connect_model_callbacks(self, app):
        return

    def _connect_index_callbacks(self, app):
        return

    def _register_blueprints(self, app):
        enabled_endpoints = app.config.get('OAREPO_FSM_ENABLED_REST_ENDPOINTS', [])
        rest_config = app.config.get('RECORDS_REST_ENDPOINTS', {})

        fsm_blueprint = Blueprint(
            'oarepo_fsm',
            __name__,
            url_prefix=''
        )

        for e in enabled_endpoints:
            econf = rest_config.get(e)
            record_class = None
            try:
                record_class: StatefulRecordMixin = econf['record_class']
            except KeyError:
                raise AttributeError('record_class must be set on RECORDS_REST_ENDPOINTS({})'.format(e))

            if not issubclass(record_class, StatefulRecordMixin):
                raise ValueError('{} must be a subclass of oarepo_fsm.mixins.StatefulRecordMixin'.format(record_class))

            fsm_url = "{0}/fsm".format(econf["item_route"])
            fsm_view_name = StatefulRecordActions.view_name.format(e, 'fsm')

            distinct_actions = record_class.get_actions()
            actions_view_name = StatefulRecordActions.view_name.format(e, 'actions')
            actions_url = "{0}/<any({1}):action>".format(
                fsm_url, ",".join([name for name, fn in distinct_actions])
            )

            view_options = dict(
                serializers=econf['record_serializers'],
                default_media_type=econf['default_media_type'],
                ctx={}
            )

            record_fsm = StatefulRecordActions.as_view(
                fsm_view_name,
                **view_options
            )

            record_actions = StatefulRecordActions.as_view(
                actions_view_name,
                **view_options
            )

            fsm_blueprint.add_url_rule(fsm_url, view_func=record_fsm, methods=["GET"])
            fsm_blueprint.add_url_rule(actions_url, view_func=record_actions, methods=["POST"])

        app.register_blueprint(fsm_blueprint)


class OARepoFSM(object):
    """oarepo-fsm extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, _app):
        """Flask application initialization."""
        self.init_config(_app)
        _state = _OARepoFSMState(_app)
        _app.extensions['oarepo-fsm'] = _state

        def app_loaded_callback(sender, app, **kwargs):
            if _app == app:
                _state.app_loaded(app)

        app_loaded.connect(app_loaded_callback, weak=False)

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith('OAREPO_FSM'):
                app.config.setdefault(k, getattr(config, k))
