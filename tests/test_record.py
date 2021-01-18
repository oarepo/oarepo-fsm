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
    record.open(id='ccc')
    assert record['state'] == 'open'

    # Test state is not changed when transition conditions are not met
    with pytest.raises(InvalidSourceStateError):
        record.open(id='aaa')
    assert record['state'] == 'open'


def test_record_transitions(record: ExampleRecord):
    assert len(record.all_transitions()) == 5
    assert 'publish' in record.all_transitions().keys()
    for trans in record.all_transitions().values():
        assert isinstance(trans, Transition)


def test_record_user_transitions(record: ExampleRecord, users):
    login_user(users['user'])
    ut = record.available_user_transitions()
    assert len(ut.items()) == 2
    assert 'open' in ut.keys()

    login_user(users['editor'])
    ut = record.all_user_transitions()
    assert set(ut.keys()) == {'close', 'delete', 'open', 'publish'}

    ut = record.available_user_transitions()
    assert set(ut.keys()) == {'open', 'delete'}

    login_user(users['admin'])
    ut = record.all_user_transitions()
    assert set(ut.keys()) == {'delete', 'archive', 'close', 'open', 'publish'}

    ut = record.available_user_transitions()
    assert set(ut.keys()) == {'delete', 'archive', 'open'}



