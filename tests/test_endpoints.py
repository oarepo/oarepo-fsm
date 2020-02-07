# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from __future__ import absolute_import, print_function

import re

from flask import url_for
from invenio_pidstore.models import PersistentIdentifier

from tests.helpers import header_links


def stringify_functions(x):
    if isinstance(x, list):
        for yy in x:
            stringify_functions(yy)
        return x
    if not isinstance(x, dict):
        return x
    for k, v in list(x.items()):
        if callable(v):
            x[k] = re.sub(r' at 0x[0-9a-fA-F]*>', r'>', str(v))
        else:
            stringify_functions(v)
    return x


def test_endpoint_rest(app, db, client, test_users, test_record):
    url = url_for('invenio_records_rest.records_list')
    resp = client.get(url)
    assert resp.status_code == 200
    server_name = app.config['SERVER_NAME']
    assert (server_name + url) in header_links(resp)['self']

    pid = PersistentIdentifier.query.filter(
        PersistentIdentifier.object_uuid == test_record.id,
    ).one()
    # record_uuid = PersistentIdentifier.get('recid', rec[0].id).object_uuid
    url = url_for('invenio_records_rest.records_item', pid_value=pid.pid_value)
    resp = client.get(url + '/fsm')
    assert resp.status_code == 200
