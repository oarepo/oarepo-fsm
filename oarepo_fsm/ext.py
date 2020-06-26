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

from . import config
from .api import after_record_insert_callback, before_record_index_callback
from .utils import convert_relative_schema_to_absolute, pid_getter
from .views import FSMRecordAction


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
        after_record_insert.connect(after_record_insert_callback)

    def _connect_index_callbacks(self, app):
        def _fsm_enabled_record_condition(sender, connect_kwargs, **signal_kwargs):
            # "connect_kwargs" are keyword arguments passed to ".dynamic_connect()
            # "signal_kwargs" are keyword arguemtns passed by the
            # "before_record_index.send()" call
            # TODO: fix teh condition
            return signal_kwargs['index'] == 'records-v1.0.0'

        before_record_index.dynamic_connect(
            before_record_index_callback,
            sender=app, condition_func=_fsm_enabled_record_condition)

    def _register_blueprints(self, app):
        endpoint_configs = app.config.get('OAREPO_FSM_ENABLED_RECORDS_REST_ENDPOINTS', {})

        fsm_blueprint = Blueprint(
            'oarepo_fsm',
            __name__,
            url_prefix='/'
        )

        for prefix, config in endpoint_configs.items():
            record_list_url = url_for(
                'invenio_records_rest.{0}_list'.format(prefix),
                _external=False)
            fsm_blueprint.add_url_rule(
                rule=f'{record_list_url}{pid_getter(config)}/fsm',
                view_func=FSMRecordAction.as_view(
                    FSMRecordAction.view_name.format(prefix),
                    fsm_pid_type=config['pid_type'],
                ))

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
