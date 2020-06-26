
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
from invenio_records_rest.utils import allow_all

from examples.models import ExampleRecord
from .helpers import test_views_permissions_factory, record_pid_minter


@pytest.fixture(scope="module")
def create_app():
    """Return API app."""
    return create_api


@pytest.fixture(scope="module")
def app_config(app_config):
    """Flask application fixture."""
    app_config["JSONSCHEMAS_ENDPOINT"] = "/schema"
    app_config["JSONSCHEMAS_HOST"] = "localhost:5000"
    app_config["RECORDS_REST_DEFAULT_READ_PERMISSION_FACTORY"] = allow_all
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


@pytest.fixture(scope="session")
def test_data():
    """Load test records."""
    path = "data/loans.json"
    with open(join(dirname(__file__), path)) as fp:
        loans = json.load(fp)
    yield loans


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
        manager = datastore.create_user(
            email="manager@test.com", password="123456", active=True
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
        manager_role = Role(name="manager")
        db.session.add(
            ActionRoles(action=authenticated_user.value, role=manager_role)
        )
        datastore.add_role_to_user(manager, manager_role)
    db.session.commit()

    return {"admin": admin, "manager": manager, "user": user}
