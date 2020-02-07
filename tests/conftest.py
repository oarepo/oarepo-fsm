# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

from __future__ import absolute_import, print_function

import os
import shutil
import sys

import pytest
from flask import Flask
from flask_principal import Principal
from invenio_base.signals import app_loaded
from invenio_db import db as _db, InvenioDB
from invenio_indexer import InvenioIndexer
from invenio_indexer.api import RecordIndexer
from invenio_records_rest.utils import allow_all
from invenio_search import InvenioSearch, RecordsSearch
from sqlalchemy_utils import database_exists, create_database

from oarepo_fsm.links import fsm_links_factory

#
@pytest.fixture
def db(app):
    """Create database for the tests."""
    # _db = SQLAlchemy(app)
    with app.app_context():
        if not database_exists(str(_db.engine.url)) and \
            app.config['SQLALCHEMY_DATABASE_URI'] != 'sqlite://':
            create_database(_db.engine.url)
        _db.create_all()

    yield _db

    # Explicitly close DB connection
    _db.session.close()
    _db.drop_all()


@pytest.yield_fixture()
def client(app):
    """Get test client."""
    with app.test_client() as client:
        yield client


@pytest.fixture()
def b_app():
    """Base Flask application fixture."""
    instance_path = os.path.join(sys.prefix, 'var', 'test-instance')

    # empty the instance path
    if os.path.exists(instance_path):
        shutil.rmtree(instance_path)
    os.makedirs(instance_path)

    os.environ['INVENIO_INSTANCE_PATH'] = instance_path

    app_ = Flask('examples-testapp', instance_path=instance_path)
    app_.config.update(
        TESTING=True,
        JSON_AS_ASCII=True,
        SQLALCHEMY_TRACK_MODIFICATIONS=True,
        SQLALCHEMY_ECHO=True,
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI',
            'sqlite:///:memory:'),
        SERVER_NAME='localhost:5000',
        SECURITY_PASSWORD_SALT='TEST_SECURITY_PASSWORD_SALT',
        SECRET_KEY='TEST_SECRET_KEY',
        INVENIO_INSTANCE_PATH=instance_path,
        SEARCH_INDEX_PREFIX='test-',
        INDEXER_DEFAULT_INDEX="examples-stateful-record-v1.0.0",
        JSONSCHEMAS_HOST='localhost:5000',
        PIDSTORE_RECID_FIELD='id',
        SEARCH_ELASTIC_HOSTS=os.environ.get('SEARCH_ELASTIC_HOSTS', None),
        RECORDS_REST_ENDPOINTS=dict(
            records=dict(
                pid_type='recid',
                pid_minter='recid',
                pid_fetcher='recid',
                search_class=RecordsSearch,
                indexer_class=RecordIndexer,
                search_index=None,
                default_endpoint_prefix=True,
                search_type=None,
                links_factory_imp=fsm_links_factory,
                record_serializers={
                    'application/json': ('invenio_records_rest.serializers'
                                         ':json_v1_response'),
                },
                search_serializers={
                    'application/json': ('invenio_records_rest.serializers'
                                         ':json_v1_search'),
                },
                list_route='/records/',
                item_route='/records/<pid(recid):pid_value>',
                default_media_type='application/json',
                max_result_window=10000,
                error_handlers=dict(),
            ),
        ),
        OAREPO_FSM_ENABLED_RECORDS_REST_ENDPOINTS={
            'records': {
                'initial_state': 'opened',
                'json_schemas': [
                    'https://localhost:5000/schemas/stateful-record-v1.0.0.json'
                ],
                'record_class': 'examples.models.ExampleRecord',
                'pid_type': 'recid',
                'transition_permission_factory': allow_all,
                'fsm_permission_factory': allow_all,
            },
        },
    )

    InvenioDB(app_)
    InvenioIndexer(app_)
    InvenioSearch(app_)
    return app_


@pytest.yield_fixture()
def app(b_app):
    """Flask application fixture."""
    # base_app._internal_jsonschemas = InvenioJSONSchemas(base_app)
    # InvenioREST(base_app)
    # InvenioPIDStore(base_app)
    # base_app.url_map.converters['pid'] = PIDConverter
    # InvenioRecordsREST(base_app)
    # InvenioRecords(base_app)
    # base_app.register_blueprint(create_blueprint_from_app(base_app))

    # OARepoFSM(base_app)

    principal = Principal(b_app)

    # login_manager = LoginManager()
    # login_manager.init_app(base_app)
    # login_manager.login_view = 'login'

    # @login_manager.user_loader
    # def basic_user_loader(user_id):
    #     user_obj = User.query.get(int(user_id))
    #     return user_obj

    # @base_app.route('/test/login/<int:id>', methods=['GET', 'POST'])
    # def test_login(id):
    #     print("test: logging user with id", id)
    #     response = make_response()
    #     user = User.query.get(id)
    #     login_user(user)
    #     set_identity(user)
    #     return response

    app_loaded.send(None, app=b_app)

    with b_app.app_context():
        yield b_app
