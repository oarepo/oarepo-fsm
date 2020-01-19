# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# examples is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions"""

from __future__ import absolute_import, print_function

import copy

from flask import Blueprint, url_for
from invenio_base.signals import app_loaded
from invenio_indexer.signals import before_record_index
from invenio_records.signals import after_record_insert
from invenio_records_rest import current_records_rest
from invenio_records_rest.utils import build_default_endpoint_prefixes
from invenio_records_rest.views import create_url_rules

from . import config
from .endpoints import create_fsm_endpoint, pid_getter
from .signals import before_record_index_callback, after_record_insert_callback
from .utils import get_search_index
from .views import FSMRecordAction


class _OARepoFSMState(object):
    """examples state object."""

    def __init__(self, app):
        """Initialize state."""
        self.app = app
        self._fsm_endpoints = {}

    @property
    def fsm_endpoints(self):
        return self._fsm_endpoints

    def app_loaded(self, app):
        with app.app_context():
            self._register_blueprints(app)
            self._connect_model_callbacks(app)
            self._connect_index_callbacks(app)

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
        if 'invenio_records_rest' not in app.blueprints:
            return

        permission_factories = {}
        endpoint_configs = app.config.get('OAREPO_FSM_ENABLED_RECORDS_REST_ENDPOINTS', {})

        rest_blueprint = app.blueprints['invenio_records_rest']
        last_deferred_function_index = len(rest_blueprint.deferred_functions)

        for url_prefix, config in endpoint_configs.items():
            config = copy.copy(config)

            json_schemas = config.pop('json_schemas', [])
            if not isinstance(json_schemas, (list, tuple)):
                json_schemas = [json_schemas]

            fsm_endpoint = f'state_{url_prefix}'
            record_endpoint = url_prefix
            record_marshmallow = config.pop('record_marshmallow')
            record_pid_type = config.pop('record_pid_type')

            fsm_index = (
                config.pop('fsm_search_index', None) or
                config.pop('search_index', None)
            )

            if not fsm_index:
                fsm_index = get_search_index(json_schemas, url_prefix)

            transition_permission_factory = config.pop('transition_permission_factory')
            fsm_permission_factory = config.pop('fsm_permission_factory')

            permission_factories[url_prefix] = {
                'transition_permission_factory': transition_permission_factory,
                'fsm_permission_factory': fsm_permission_factory,
            }

            fsm_endpoint_config = create_fsm_endpoint(
                url_prefix=url_prefix,
                fsm_endpoint=fsm_endpoint,
                record_endpoint=record_endpoint,
                record_pid_type=record_pid_type,
                search_index=fsm_index,
                record_marshmallow=record_marshmallow,
                transition_permission_factory=transition_permission_factory,
                fsm_permission_factory=fsm_permission_factory,
                **config
            )

            for rule in create_url_rules(fsm_endpoint, **fsm_endpoint_config):
                rest_blueprint.add_url_rule(**rule)

            default_prefixes = build_default_endpoint_prefixes({
                fsm_endpoint: fsm_endpoint_config,
            })
            current_records_rest.default_endpoint_prefixes.update(default_prefixes)
            fsm_endpoint_config['endpoint'] = fsm_endpoint
            fsm_endpoint_config['fsm_record_class'] = config.pop('fsm_record_class')
            self.fsm_endpoints[url_prefix] = {
                **fsm_endpoint_config,
                **permission_factories[url_prefix]
            }

        state = rest_blueprint.make_setup_state(app, {}, False)
        for deferred in rest_blueprint.deferred_functions[last_deferred_function_index:]:
            deferred(state)

        fsm_blueprint = Blueprint(
            'oarepo_fsm',
            __name__,
            url_prefix='/'
        )

        for prefix, config in self.fsm_endpoints.items():
            fsm_endpoint_name = config['endpoint']
            permissions = permission_factories[prefix]

            fsm_url = url_for(
                'invenio_records_rest.{0}_list'.format(fsm_endpoint_name),
                _external=False)

            fsm_blueprint.add_url_rule(
                rule=f'{fsm_url}{pid_getter(config)}/fsm',
                view_func=FSMRecordAction.as_view(
                    FSMRecordAction.view_name.format(fsm_endpoint_name),
                    fsm_permission_factory=permissions['fsm_permission_factory'],
                    transition_permission_factory=permissions['transition_permission_factory'],
                    fsm_record_class=config['fsm_record_class'],
                    fsm_pid_type=config['pid_type'],
                    fsm_endpoint_name=fsm_endpoint_name
                ))

            app.register_blueprint(fsm_blueprint)


class OARepoFSM(object):
    """examples extension."""

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

        app.config['RECORDS_REST_ENDPOINTS'] = {}
