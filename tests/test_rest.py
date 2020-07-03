# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Test StatefulRecord REST API."""
import json

from flask import url_for
from invenio_pidstore.fetchers import recid_fetcher_v2

from examples import ExampleRecord
from oarepo_fsm.views import build_url_action_for_pid


def test_record_rest_endpoints(app, json_headers):
    """Test REST API FSM endpoints."""
    url_rules = [r.rule for r in app.url_map.iter_rules()]
    url_endpoints = [r.endpoint for r in app.url_map.iter_rules()]
    assert '/records/<pid(recid,record_class="examples.models:ExampleRecord"):pid_value>/fsm' in url_rules
    assert '/records/<pid(recid,record_class="examples.models:ExampleRecord"):pid_value>/fsm/' \
           '<any(archive,close,open,publish):action>' in url_rules
    assert 'oarepo_fsm.recid_fsm' in url_endpoints
    assert 'oarepo_fsm.recid_actions' in url_endpoints


def test_fsm_rest_get(app, json_headers, record, users, test_blueprint):
    """TEST FSM REST API logged in as certain users."""
    recpid = recid_fetcher_v2(record.id, record)

    test_cases = [
        (users['user'],
         {
             'actions': {
                 'open': build_url_action_for_pid(recpid, 'open'),
                 'close': build_url_action_for_pid(recpid, 'close')
             }
         }),
        (users['editor'],
         {
             'actions': {
                 'open': build_url_action_for_pid(recpid, 'open'),
                 'close': build_url_action_for_pid(recpid, 'close'),
                 'publish': build_url_action_for_pid(recpid, 'publish')
             }
         }),
        (users['admin'],
         {
             'actions': {
                 'open': build_url_action_for_pid(recpid, 'open'),
                 'close': build_url_action_for_pid(recpid, 'close'),
                 'publish': build_url_action_for_pid(recpid, 'publish'),
                 'archive': build_url_action_for_pid(recpid, 'archive')
             }
         })
    ]

    url = url_for('oarepo_fsm.recid_fsm',
                  pid_value=recid_fetcher_v2(record.id, record).pid_value)

    for user, expected_links in test_cases:
        with app.test_client() as client:
            client.get(url_for('_tests.test_login_{}'.format(user.id)))
            res = client.get(url, headers=json_headers)

        assert res.status_code == 200
        res_dict = json.loads(res.data.decode('utf-8'))
        assert res_dict['metadata']['state'] == record['state']
        assert res_dict['links'] == expected_links


def test_fsm_rest_post(app, json_headers, record, users, test_blueprint):
    """TEST FSM REST API logged in as certain users."""
    test_cases = [
        (users['user'],
         ['open', 'close', 'publish'],
         [
             (202, {'metadata': {'pid': '2', 'state': 'open', 'title': 'example'}}),
             (202, {'metadata': {'pid': '2', 'state': 'closed', 'title': 'example'}}),
             (404, {'message': 'Action publish is not available on this record'})
         ]),
        (users['editor'],
         ['open', 'close', 'publish'],
         [
             (202, {'metadata': {'pid': '2', 'state': 'open', 'title': 'example'}}),
             (202, {'metadata': {'pid': '2', 'state': 'closed', 'title': 'example'}}),
             (400, {'message': 'Transition from closed to published is not allowed'})
         ]),
        (users['admin'],
         ['open', 'close', 'archive', 'publish'],
         [
             (202, {'metadata': {'pid': '2', 'state': 'open', 'title': 'example'}}),
             (202, {'metadata': {'pid': '2', 'state': 'closed', 'title': 'example'}}),
             (202, {'metadata': {'pid': '2', 'state': 'archived', 'title': 'example'}}),
             (202, {'metadata': {'pid': '2', 'state': 'published', 'title': 'example'}})
         ])
    ]

    for user, actions, expected_results in test_cases:
        with app.test_client() as client:
            client.get(url_for('_tests.test_login_{}'.format(user.id)))
            for idx, action in enumerate(actions):
                expected_status, expected_body = expected_results[idx]

                url = url_for('oarepo_fsm.recid_actions',
                              action=action,
                              pid_value=recid_fetcher_v2(record.id, record).pid_value)

                res = client.post(url, headers=json_headers)
                res_dict = json.loads(res.data.decode('utf-8'))
                assert res.status_code == expected_status
                for k, v in expected_body.items():
                    assert res_dict[k] == v


def test_rest_state_change_prevented(app, record, users, json_patch_headers, test_blueprint):
    url = url_for('invenio_records_rest.recid_item',
                  pid_value=recid_fetcher_v2(record.id, record).pid_value)

    orig_state = record['state']

    with app.test_client() as client:
        client.get(url_for('_tests.test_login_{}'.format(users['admin'].id)))
        res = client.patch(
            url,
            json=[{"op": "replace", "path": "/state", "value": "boo"}],
            headers=json_patch_headers)

        assert res.status_code == 403
        rec = ExampleRecord.get_record(record.id)
        assert rec['state'] == record['state']
