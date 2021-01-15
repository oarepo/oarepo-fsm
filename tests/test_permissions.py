# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Test transition permissions."""
import pytest
from flask_security import login_user

from examples.models import ExampleRecord
from oarepo_fsm.errors import InvalidPermissionError
from oarepo_fsm.permissions import require_all, require_any, state_required, \
    transition_required


def test_transition_permissions(record: ExampleRecord, users):
    # Regular user can neither publish, nor archive
    login_user(users['user'])
    assert record['state'] == 'closed'
    with pytest.raises(InvalidPermissionError):
        record.archive()

    record.open(id='abc')
    with pytest.raises(InvalidPermissionError):
        record.publish()
    record.close(id=4)

    # User editor can publish, but not archive record
    login_user(users['editor'])
    assert record['state'] == 'closed'
    record.open(id='bca')
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


def test_state_required(record: ExampleRecord, users):
    assert state_required('closed')(record).can()
    assert not state_required('editing')(record).can()


def test_require_all(record: ExampleRecord):
    assert not require_all(
        state_required('closed'),
        state_required('editing'),
    )(record).can()

    assert require_all(
        state_required('closed'),
        state_required('editing', 'closed'),
    )(record).can()

    assert not require_all()(record).can()


def test_require_any(record: ExampleRecord):
    assert not require_any(
        state_required('new'),
        state_required('editing'),
    )(record).can()

    assert require_any(
        state_required('closed'),
        state_required('editing'),
    )(record).can()

    assert not require_any()(record).can()


def test_transition_required(record: ExampleRecord, users):
    # Regular user can neither publish, nor archive, but can open
    login_user(users['user'])
    assert not transition_required('archive')(record).can()
    assert not transition_required('publish')(record).can()
    assert transition_required('open')(record).can()

    # User editor can publish, but not archive record
    login_user(users['editor'])
    assert not transition_required('archive')(record).can()
    assert not transition_required('publish')(record).can()
    record['state'] = 'open'
    assert transition_required('publish')(record).can()

    # User with admin role can both archive and publish
    login_user(users['admin'])
    record['state'] = 'closed'
    assert transition_required('archive')(record).can()
    assert not transition_required('publish')(record).can()

    record['state'] = 'published'
    assert transition_required('archive')(record).can()
    assert not transition_required('publish')(record).can()
