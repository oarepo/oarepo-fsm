# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions."""

from __future__ import absolute_import, print_function

from flask import Blueprint
from invenio_base.signals import app_loaded
from invenio_records_rest.utils import obj_or_import_string

from . import config
from .mixins import FSMMixin
from .views import FSMRecordTransitions
from invenio_indexer.api import RecordIndexer


class _OARepoFSMState(object):
    """oarepo-fsm state object."""

    def __init__(self, app):
        """Initialize state."""
        self.app = app
        self.schema_map = {}

    def app_loaded(self, app):
        with app.app_context():
            self._register_blueprints(app)

    def _register_blueprints(self, app):
        enabled_endpoints = app.config.get('OAREPO_FSM_ENABLED_REST_ENDPOINTS', [])
        rest_config = app.config.get('RECORDS_REST_ENDPOINTS', {})

        fsm_blueprint = Blueprint(
            'oarepo_fsm',
            __name__,
            url_prefix=''
        )

        if not enabled_endpoints:
            # Auto-enable endpoints using FSM-enabled record_class
            for end, conf in rest_config.items():
                record_class = obj_or_import_string(conf['record_class'])
                if issubclass(record_class, FSMMixin):
                    enabled_endpoints.append(end)

        for e in enabled_endpoints:
            econf = rest_config.get(e)
            record_class = None
            try:
                record_class: FSMMixin = obj_or_import_string(econf['record_class'])
            except KeyError:
                raise AttributeError('record_class must be set on RECORDS_REST_ENDPOINTS({})'.format(e))

            if not issubclass(record_class, FSMMixin):
                raise ValueError('{} must be a subclass of oarepo_fsm.mixins.FSMMixin'.format(record_class))

            indexer_class = obj_or_import_string(econf.get('indexer_class', RecordIndexer))

            fsm_url = econf["item_route"]
            fsm_view_name = FSMRecordTransitions.view_name.format(econf['pid_type'], 'fsm')

            distinct_transitions = record_class.all_transitions()
            transitions_view_name = FSMRecordTransitions.view_name.format(econf['pid_type'], 'transitions')
            transitions_url = "{0}/<any({1}):transition>".format(
                fsm_url, ",".join([name for name, fn in distinct_transitions.items()])
            )

            serializers = {}
            for k, v in econf['record_serializers'].items():
                serializers[k] = obj_or_import_string(v)

            view_options = dict(
                serializers=serializers,
                indexer_class=indexer_class,
                default_media_type=econf['default_media_type'],
                ctx={}
            )

            record_transitions = FSMRecordTransitions.as_view(
                transitions_view_name,
                **view_options
            )

            fsm_blueprint.add_url_rule(transitions_url, view_func=record_transitions, methods=["POST"])

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
