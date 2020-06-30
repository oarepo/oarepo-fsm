
"""Pytest configuration."""

from __future__ import absolute_import, print_function

import json
import uuid
from os.path import dirname, join

import pytest
from invenio_access import ActionRoles, superuser_access, authenticated_user
from invenio_accounts.models import Role
from invenio_app.factory import create_api
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_records_rest.utils import allow_all
from invenio_search import RecordsSearch

from examples.models import ExampleRecord
from .helpers import test_views_permissions_factory, record_pid_minter


@pytest.fixture(scope='module')
def create_app():
    """Return API app."""
    return create_api


@pytest.fixture(scope='module')
def app_config(app_config):
    """Flask application fixture."""
    app_config["JSONSCHEMAS_ENDPOINT"] = '/schema'
    app_config["JSONSCHEMAS_HOST"] = 'localhost:5000'
    app_config['RECORDS_REST_DEFAULT_READ_PERMISSION_FACTORY'] = allow_all
    app_config['OAREPO_FSM_ENABLED_REST_ENDPOINTS'] = ['recid']
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
            item_route='/records/<pid(recid):pid_value>',
            default_media_type='application/json',
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

    record_pid_minter(record_uuid, data=new_record)
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


# @pytest.fixture()
# def test_records(db, test_data):
#     """Load test records."""
#     loans = []
#     for data in test_data:
#         loans.append(create_loan(data))
#     db.session.commit()
#     yield loans


# @pytest.fixture()
# def indexed_records(es, test_records):
#     """Get a function to wait for records to be flushed to index."""
#     indexer = RecordIndexer()
#     for pid, record in test_records:
#         indexer.index(record)
#     current_search.flush_and_refresh(index="records")
#
#     yield test_records
#
#     for pid, record in test_records:
#         indexer.delete_by_id(record.id)
#     current_search.flush_and_refresh(index="records")


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
