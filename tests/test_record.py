# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Test StatefulRecord mixin."""

import pytest
from flask_security import login_user

from examples.models import ExampleRecord
from oarepo_fsm.decorators import Transition
from oarepo_fsm.errors import InvalidSourceStateError


def test_record_transition(record: ExampleRecord):
    # Test state is changed when transition conditions are met
    assert record['state'] == 'closed'
    record.open()
    assert record['state'] == 'open'

    # Test state is not changed when transition conditions are not met
    with pytest.raises(InvalidSourceStateError):
        record.open()
    assert record['state'] == 'open'


def test_record_states(record: ExampleRecord):
    assert len(record.actions().items()) == 4
    assert 'publish' in record.actions().keys()


def test_record_transitions(record: ExampleRecord):
    assert len(record.transitions()) == 4
    for trans in record.transitions().values():
        assert isinstance(trans, Transition)


def test_record_user_transitions(record: ExampleRecord, users):
    login_user(users['user'])
    ut = record.user_actions()
    assert len(ut.items()) == 2
    assert 'close' in ut.keys()
    assert 'open' in ut.keys()

    login_user(users['editor'])
    ut = record.user_actions()
    assert len(ut.items()) == 3
    assert list(ut.keys()) == ['close', 'open', 'publish']

    login_user(users['admin'])
    ut = record.user_actions()
    assert len(ut.items()) == 4
    assert list(ut.keys()) == ['archive', 'close', 'open', 'publish']
