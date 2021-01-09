#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions test module."""

from __future__ import absolute_import, print_function

import uuid

import pytest
from flask import Blueprint
from invenio_access import ActionRoles, authenticated_user, superuser_access
from invenio_accounts.models import Role
from invenio_app.factory import create_api
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_records_rest.utils import allow_all
from invenio_search import RecordsSearch

from examples.models import ExampleRecord

from .helpers import _test_login_factory, record_pid_minter, \
    test_views_permissions_factory


@pytest.fixture(scope='session')
def create_app():
    """Return API app."""
    return create_api


@pytest.fixture(scope='session')
def celery_config():
    """Celery app test configuration."""
    return {
        'broker_url': 'memory://localhost/',
        'result_backend': 'rpc'
    }


@pytest.fixture(scope='module')
def app_config(app_config):
    """Flask application fixture."""
    app_config['JSONSCHEMAS_ENDPOINT'] = '/schema'
    app_config['JSONSCHEMAS_HOST'] = 'localhost:5000'
    app_config['PIDSTORE_RECID_FIELD'] = 'pid'
    app_config['RECORDS_REST_DEFAULT_READ_PERMISSION_FACTORY'] = allow_all
    app_config['OAREPO_FSM_ENABLED_REST_ENDPOINTS'] = []
    app_config['RECORDS_REST_ENDPOINTS'] = dict(
        recid=dict(
            pid_type='recid',
            pid_minter='recid',
            pid_fetcher='recid',
            search_class=RecordsSearch,
            indexer_class=RecordIndexer,
            record_class=ExampleRecord,
            search_index=None,
            default_endpoint_prefix=True,
            search_type=None,
            record_serializers={
                'application/json': ('invenio_records_rest.serializers'
                                     ':json_v1_response'),
            },
            search_serializers={
                'application/json': ('invenio_records_rest.serializers'
                                     ':json_v1_search'),
            },
            list_route='/records/',
            links_factory_imp='oarepo_fsm.links:record_fsm_links_factory',
            item_route='/records/<pid(recid,record_class="examples.models:ExampleRecord"):pid_value>',
            default_media_type='application/json',
            create_permission_factory_imp=allow_all,
            delete_permission_factory_imp=allow_all,
            update_permission_factory_imp=allow_all,
            read_permission_factory_imp=allow_all,
            max_result_window=10000,
            error_handlers=dict(),
        ),
    )
    return app_config


@pytest.fixture()
def record(app):
    """Minimal Record object."""
    record_uuid = uuid.uuid4()
    new_record = {
        'title': 'example',
        'state': 'closed'
    }

    pid = record_pid_minter(record_uuid, data=new_record)
    record = ExampleRecord.create(data=new_record, id_=record_uuid)

    db.session.commit()
    yield record


@pytest.fixture()
def json_headers(app):
    """JSON headers."""
    return [
        ("Content-Type", "application/json"),
        ("Accept", "application/json"),
    ]


@pytest.fixture()
def json_patch_headers(app):
    """JSON Patch headers."""
    return [
        ('Content-Type', 'application/json-patch+json'),
        ('Accept', 'application/json'),
    ]


@pytest.fixture()
def users(db, base_app):
    """Create admin, manager and user."""
    base_app.config[
        "OAREPO_FSM_PERMISSIONS_FACTORY"
    ] = test_views_permissions_factory

    with db.session.begin_nested():
        datastore = base_app.extensions["security"].datastore

        # create users
        editor = datastore.create_user(
            email="editor@test.com", password="123456", active=True
        )
        admin = datastore.create_user(
            email="admin@test.com", password="123456", active=True
        )
        user = datastore.create_user(
            email="user@test.com", password="123456", active=True
        )

        # Give role to admin
        admin_role = Role(name="admin")
        db.session.add(
            ActionRoles(action=superuser_access.value, role=admin_role)
        )
        datastore.add_role_to_user(admin, admin_role)
        # Give role to user
        editor_role = Role(name="editor")
        db.session.add(
            ActionRoles(action=authenticated_user.value, role=editor_role)
        )
        datastore.add_role_to_user(editor, editor_role)
    db.session.commit()

    return {"admin": admin, "editor": editor, "user": user}


@pytest.fixture()
def test_blueprint(users, app):
    """Test blueprint with dynamically added testing endpoints."""
    blue = Blueprint(
        '_tests',
        __name__,
        url_prefix='/_tests/'
    )

    if blue.name in app.blueprints:
        del app.blueprints[blue.name]

    for _, user in users.items():
        if app.view_functions.get('_tests.test_login_{}'.format(user.id)) is not None:
            del app.view_functions['_tests.test_login_{}'.format(user.id)]

        blue.add_url_rule('_login_{}'.format(user.id), view_func=_test_login_factory(user))

    app.register_blueprint(blue)
    return blue
