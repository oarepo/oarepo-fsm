# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Pytest helper methods."""
import copy
import uuid

from invenio_db import db
from invenio_pidstore.providers.recordid import RecordIdProvider
from invenio_records_rest.utils import allow_all

from examples.models import ExampleRecord


def test_record_transition(record: ExampleRecord, db):
    assert record['state'] == 'closed'
    record.open()
    assert record['state'] == 'open'
