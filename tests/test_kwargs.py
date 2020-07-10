# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Test transition required kwargs."""
import pytest
from flask_security import login_user

from oarepo_fsm.errors import MissingRequiredParameterError


def test_transition_kwargs(record, users):
    login_user(users['user'])
    assert record['state'] == 'closed'
    with pytest.raises(MissingRequiredParameterError):
        record.open()

    assert record['state'] == 'closed'

    record.open(id='abc')
    with pytest.raises(MissingRequiredParameterError):
        record.close()

    record.close(id='cba')
