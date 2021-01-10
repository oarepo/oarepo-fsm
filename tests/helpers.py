# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Pytest helper methods."""
import copy
import uuid

from flask_security import login_user
from invenio_db import db
from invenio_pidstore.providers.recordid import RecordIdProvider
from invenio_records_rest.utils import allow_all

from examples.models import ExampleRecord


def record_pid_minter(record_uuid, data):
    """Mint loan identifiers."""
    assert "pid" not in data
    provider = RecordIdProvider.create(
        object_type='rec',
        object_uuid=record_uuid,
    )
    data["pid"] = provider.pid.pid_value
    return provider.pid


def create_record(data):
    """Create a test record."""
    with db.session.begin_nested():
        data = copy.deepcopy(data)
        rec_uuid = uuid.uuid4()
        pid = record_pid_minter(rec_uuid, data)
        record = ExampleRecord.create(data, id_=rec_uuid)
        return pid, record


def test_views_permissions_factory(transition):
    """Test permissions factory."""
    return allow_all()


def _test_login_factory(user):
    def test_login():
        login_user(user, remember=True)
        return 'OK'

    test_login.__name__ = '{}_{}'.format(test_login.__name__, user.id)
    return test_login
