# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# examples is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from __future__ import absolute_import, print_function

import re

from flask import url_for

from oarepo_fsm.proxies import current_oarepo_fsm
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


def test_endpoint_config(app, schemas):
    fsm_endpoint = current_oarepo_fsm.fsm_endpoints['records']
    assert stringify_functions(fsm_endpoint) == {
        'create_permission_factory_imp': '<function deny_all>',
        'default_endpoint_prefix': True,
        'delete_permission_factory_imp': '<function deny_all>',
        'item_route': 'records/<pid(recid,'
                      'record_class="invenio_records.api:Record"):pid_value>',
        'list_permission_factory_imp': '<function allow_all>',
        'list_route': '/records/',
        'pid_type': 'recid',
        'pid_fetcher': 'recid',
        'pid_minter': 'recid',
        'read_permission_factory_imp': '<function allow_all>',
        'record_class': "<class 'invenio_records.api.Record'>",
        # 'record_loaders': {
        #     'application/json': '<function marshmallow_loader.<locals>.json_loader>',
        #     'application/json-patch+json': '<function json_patch_loader>'
        # },
        'record_serializers': {
            'application/json': '<function record_responsify.<locals>.view>'
        },
        'search_index': 'examples-stateful-record-v1.0.0',
        'search_serializers': {
            'application/json': '<function search_responsify.<locals>.view>'
        },
        'default_media_type': 'application/json',
        'update_permission_factory_imp': '<function allow_all>',
        'fsm_record_class': "<class 'oarepo_fsm.models.FSMRecord'>",
        'links_factory_imp':
            '<oarepo_fsm.endpoints.FSMLinksFactory object>',
        'endpoint': 'state_records',
        'transition_permission_factory': '<function allow_all>',
        'fsm_permission_factory': '<function allow_all>',
    }


def test_endpoint_rest(app, db, json_client, test_users, test_record):
    url = url_for('invenio_records_rest.state_records_list')
    resp = json_client.get(url)
    assert resp.status_code == 200
    server_name = app.config['SERVER_NAME']
    assert (server_name + url) in header_links(resp)['self']
