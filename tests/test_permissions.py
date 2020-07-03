# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Test transition permissions."""
import pytest
from examples.models import ExampleRecord
from flask_security import login_user

from oarepo_fsm.errors import InvalidPermissionError


def test_transition_permissions(record: ExampleRecord, users):
    # Regular user can neither publish, nor archive
    login_user(users['user'])
    assert record['state'] == 'closed'
    with pytest.raises(InvalidPermissionError):
        record.archive()

    record.open()
    with pytest.raises(InvalidPermissionError):
        record.publish()
    record.close()

    # User editor can publish, but not archive record
    login_user(users['editor'])
    assert record['state'] == 'closed'
    record.open()
    record.publish()
    assert record['state'] == 'published'

    with pytest.raises(InvalidPermissionError):
        record.archive()
    assert record['state'] == 'published'

    # User with admin role can both archive and publish
    login_user(users['admin'])
    record.archive()
    assert record['state'] == 'archived'
    record.publish()
    assert record['state'] == 'published'
