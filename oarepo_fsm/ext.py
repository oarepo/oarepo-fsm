# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions"""

from __future__ import absolute_import, print_function

from flask import Blueprint, url_for
from invenio_base.signals import app_loaded
from invenio_indexer.signals import before_record_index
from invenio_records import Record
from invenio_records.signals import after_record_insert
from invenio_records_rest import current_records_rest

from . import config
from .mixins import StatefulRecordMixin
from .utils import convert_relative_schema_to_absolute, pid_getter
from .views import FSMRecordAction, StatefulRecordActions


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
            self._prepare_schema_map(app)

    def get_initial_state(self, record: Record):
        config = self.schema_map.get(record['$schema'], None)
        return config.get('initial_state', 'initial')

    def get_record_fsm_prefix(self, record):
        schema = record.get('$schema', None)
        if not schema:
            return None

        schema = convert_relative_schema_to_absolute(schema)
        config = self.schema_map.get(schema, None)
        if not config:
            return None
        return config['prefix']

    def _prepare_schema_map(self, app):
        config = app.config.get('OAREPO_FSM_ENABLED_RECORDS_REST_ENDPOINTS', {})
        for prefix, item in config.items():
            schemas = item.get('json_schemas', [])
            for sch in schemas:
                self.schema_map[convert_relative_schema_to_absolute(sch)] = {'prefix': prefix, **item}

    def _connect_model_callbacks(self, app):
        return

    def _connect_index_callbacks(self, app):
        return

    def _register_blueprints(self, app):
        enabled_endpoints = app.config.get('OAREPO_FSM_ENABLED_REST_ENDPOINTS', [])
        rest_prefixes = current_records_rest.default_endpoint_prefixes
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

            distinct_actions = record_class.get_actions()
            print(list(distinct_actions))
            url = "{0}/<any({1}):action>".format(
                econf["item_route"], ",".join([name for name, fn in distinct_actions])
            )

            record_actions = StatefulRecordActions.as_view(
                StatefulRecordActions.view_name.format(e),
                **dict(
                    serializers=econf['serializers'],
                    default_media_type=econf['default_media_type'],
                    ctx={}
                )
            )

            fsm_blueprint.add_url_rule(url, view_func=record_actions, methods=["POST"])

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
