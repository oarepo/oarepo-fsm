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
    assert len(record.get_actions()) == 4
    assert 'publish' in [s[0] for s in record.get_actions()]


def test_record_transitions(record: ExampleRecord):
    assert len(record.transitions()) == 4
    for t in record.transitions():
        assert isinstance(t, Transition)


def test_record_user_transitions(record: ExampleRecord, users):
    login_user(users['user'])
    ut = list(record.user_transitions())
    assert len(ut) == 2
    assert [u.dest for u in ut] == ['closed', 'open']

    login_user(users['editor'])
    ut = list(record.user_transitions())
    assert len(ut) == 3
    assert [u.dest for u in ut] == ['closed', 'open', 'published']

    login_user(users['admin'])
    ut = list(record.user_transitions())
    assert len(ut) == 4
    assert [u.dest for u in ut] == ['archived', 'closed', 'open', 'published']
