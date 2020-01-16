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
import uuid
from collections import namedtuple

import pytest
from flask import Flask, make_response
from flask.testing import FlaskClient
from flask_login import LoginManager, login_user
from flask_principal import Principal
from invenio_accounts.models import User, Role
from invenio_base.signals import app_loaded
from invenio_db import db as _db, InvenioDB
from invenio_indexer import InvenioIndexer
from invenio_indexer.api import RecordIndexer
from invenio_jsonschemas import InvenioJSONSchemas
from invenio_pidstore.minters import recid_minter
from invenio_records import InvenioRecords, Record
from invenio_records_rest import InvenioRecordsREST
from invenio_records_rest.views import create_blueprint_from_app
from invenio_rest import InvenioREST
from invenio_search import current_search_client
from invenio_search.cli import destroy, init
from invenio_search.utils import build_index_name
from sqlalchemy_utils import database_exists, create_database

from oarepo_fsm import OARepoFSM
from tests.helpers import set_identity


class JsonClient(FlaskClient):
    """JsonClient class."""

    def open(self, *args, **kwargs):
        kwargs.setdefault('content_type', 'application/json')
        kwargs.setdefault('Accept', 'application/json')
        return super().open(*args, **kwargs)


@pytest.fixture(scope='module')
def json_client(base_client):
    """Test JSON client for the base application fixture."""
    with JsonClient() as client:
        yield client


@pytest.fixture(scope='module')
def celery_config():
    """Override pytest-invenio fixture.

    TODO: Remove this fixture if you add Celery support.
    """
    return {}


@pytest.fixture()
def base_app():
    """Base Flask application fixture."""
    instance_path = os.path.join(sys.prefix, 'var', 'test-instance')

    # empty the instance path
    if os.path.exists(instance_path):
        shutil.rmtree(instance_path)
    os.makedirs(instance_path)

    os.environ['INVENIO_INSTANCE_PATH'] = instance_path

    app_ = Flask('oarepo-fsm-testapp', instance_path=instance_path)
    app_.config.update(
        TESTING=True,
        JSON_AS_ASCII=True,
        SQLALCHEMY_TRACK_MODIFICATIONS=True,
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI',
            'sqlite:///:memory:'),
        SERVER_NAME='localhost:5000',
        SECURITY_PASSWORD_SALT='TEST_SECURITY_PASSWORD_SALT',
        SECRET_KEY='TEST_SECRET_KEY',
        INVENIO_INSTANCE_PATH=instance_path,
        SEARCH_INDEX_PREFIX='test-',
        JSONSCHEMAS_HOST='localhost:5000',
        SEARCH_ELASTIC_HOSTS=os.environ.get('SEARCH_ELASTIC_HOSTS', None)
    )
    app_.test_client_class = JsonClient

    InvenioDB(app_)
    InvenioIndexer(app_)
    print('oarepo fsm registered to app')
    OARepoFSM(app_)

    return app_


@pytest.yield_fixture()
def app(base_app):
    """Flask application fixture."""

    base_app._internal_jsonschemas = InvenioJSONSchemas(base_app)
    InvenioREST(base_app)
    InvenioRecordsREST(base_app)
    InvenioRecords(base_app)

    base_app.register_blueprint(create_blueprint_from_app(base_app))

    principal = Principal(base_app)

    login_manager = LoginManager()
    login_manager.init_app(base_app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def basic_user_loader(user_id):
        user_obj = User.query.get(int(user_id))
        return user_obj

    @base_app.route('/test/login/<int:id>', methods=['GET', 'POST'])
    def test_login(id):
        print("test: logging user with id", id)
        response = make_response()
        user = User.query.get(id)
        login_user(user)
        set_identity(user)
        return response

    app_loaded.send(None, app=base_app)

    with base_app.app_context():
        yield base_app


@pytest.yield_fixture()
def client(app):
    """Get test client."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def db(app):
    """Create database for the tests."""
    with app.app_context():
        if not database_exists(str(_db.engine.url)) and \
          app.config['SQLALCHEMY_DATABASE_URI'] != 'sqlite://':
            create_database(_db.engine.url)
        _db.create_all()

    yield _db

    # Explicitly close DB connection
    _db.session.close()
    _db.drop_all()


@pytest.fixture
def schemas(app):
    # trigger registration of new schemas, normally performed
    # via app_loaded signal that is not emitted in tests
    with app.app_context():
        # TODO: register schemas
        pass

    return {
        'oarepo-fsm-test':
            'https://localhost:5000/schemas/oarepo-fsm-test-v1.0.0.json',
    }


@pytest.fixture
def mappings(app, schemas):
    # trigger registration of new schemas, normally performed
    # via app_loaded signal that is not emitted in tests
    with app.app_context():
        current_search_client.mappings['oarepo-fsm-test-v.1.0.0'] =\
            'schemas/oarepo-fsm-test-v1.0.0.json'


@pytest.fixture()
def prepare_es(app, db):
    runner = app.test_cli_runner()
    result = runner.invoke(destroy, ['--yes-i-know', '--force'])
    if result.exit_code:
        print(result.output, file=sys.stderr)
    assert result.exit_code == 0
    result = runner.invoke(init)
    if result.exit_code:
        print(result.output, file=sys.stderr)
    assert result.exit_code == 0
    aliases = current_search_client.indices.get_mapping("*")

    assert build_index_name('oarepo-fsm-test-v1.0.0') in aliases


TestUsers = namedtuple('TestUsers', ['u1', 'u2', 'u3', 'r1', 'r2'])


@pytest.fixture()
def test_users(app, db):
    """Returns named tuple (u1, u2, u3, r1, r2)."""
    with db.session.begin_nested():
        r1 = Role(name='role1')
        r2 = Role(name='role2')

        u1 = User(id=1, email='1@test.com', active=True, roles=[r1])
        u2 = User(id=2, email='2@test.com', active=True, roles=[r1, r2])
        u3 = User(id=3, email='3@test.com', active=True, roles=[r2])

        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)

        db.session.add(r1)
        db.session.add(r2)

    return TestUsers(u1, u2, u3, r1, r2)


@pytest.fixture(scope='function')
def test_record(app, db, schemas):
    # let's create a record
    record_uuid = uuid.uuid4()
    data = {
        'title': 'blah',
        '$schema': schemas['oarepo-fsm-test'],
    }
    recid_minter(record_uuid, data)
    rec = Record.create(data, id_=record_uuid)
    RecordIndexer().index(rec)
    current_search_client.indices.refresh()
    current_search_client.indices.flush()

    return rec
