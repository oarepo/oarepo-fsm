# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Test StatefulRecord REST API."""
import json

from examples import ExampleRecord
from flask import url_for
from invenio_pidstore.fetchers import recid_fetcher_v2

from oarepo_fsm.views import build_url_action_for_pid


def test_record_rest_endpoints(app, json_headers):
    """Test REST API FSM endpoints."""
    url_rules = [r.rule for r in app.url_map.iter_rules()]
    url_endpoints = [r.endpoint for r in app.url_map.iter_rules()]
    assert '/records/<pid(recid,record_class="examples.models:ExampleRecord"):pid_value>' in url_rules
    assert '/records/<pid(recid,record_class="examples.models:ExampleRecord"):pid_value>/' \
           '<any(archive,close,open,publish):action>' in url_rules
    assert 'oarepo_fsm.recid_fsm' in url_endpoints
    assert 'oarepo_fsm.recid_actions' in url_endpoints


def test_fsm_rest_get(app, json_headers, record, users, test_blueprint):
    """TEST FSM REST API logged in as certain users."""
    recpid = recid_fetcher_v2(record.id, record)

    test_cases = [
        (users['user'],
         {
             'open': build_url_action_for_pid(recpid, 'open'),
             'close': build_url_action_for_pid(recpid, 'close'),
             'self': url_for('oarepo_fsm.recid_fsm', _external=True,
                             pid_value=recid_fetcher_v2(record.id, record).pid_value)
         }),
        (users['editor'],
         {
             'open': build_url_action_for_pid(recpid, 'open'),
             'close': build_url_action_for_pid(recpid, 'close'),
             'publish': build_url_action_for_pid(recpid, 'publish'),
             'self': url_for('oarepo_fsm.recid_fsm', _external=True,
                             pid_value=recid_fetcher_v2(record.id, record).pid_value)
         }),
        (users['admin'],
         {

             'open': build_url_action_for_pid(recpid, 'open'),
             'close': build_url_action_for_pid(recpid, 'close'),
             'publish': build_url_action_for_pid(recpid, 'publish'),
             'archive': build_url_action_for_pid(recpid, 'archive'),
             'self': url_for('oarepo_fsm.recid_fsm', _external=True,
                             pid_value=recid_fetcher_v2(record.id, record).pid_value)
         })
    ]

    url = url_for('oarepo_fsm.recid_fsm',
                  pid_value=recid_fetcher_v2(record.id, record).pid_value) \
        .replace('/api', '')

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
         [('open', {'id': 1}), ('close', {'id': 1}), ('publish', {})],
         [
             (202, {'metadata': {'pid': '2', 'state': 'open', 'title': 'example'}}),
             (202, {'metadata': {'pid': '2', 'state': 'closed', 'title': 'example'}}),
             (404, {'message': 'Action publish is not available on this record'})
         ]),
        (users['editor'],
         [('open', {'id': 2}), ('close', {'id': 2}), ('publish', {})],
         [
             (202, {'metadata': {'pid': '2', 'state': 'open', 'title': 'example'}}),
             (202, {'metadata': {'pid': '2', 'state': 'closed', 'title': 'example'}}),
             (400, {'message': 'Transition from closed to published is not allowed'})
         ]),
        (users['admin'],
         [('open', {'id': 3}), ('close', {'id': 3}), ('archive', {}), ('publish', {})],
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
                actname, kwargs = action

                url = url_for('oarepo_fsm.recid_actions',
                              action=actname,
                              pid_value=recid_fetcher_v2(record.id, record).pid_value) \
                    .replace('/api', '')
                print(url)
                res = client.post(url, json={**kwargs}, headers=json_headers)
                res_dict = json.loads(res.data.decode('utf-8'))
                assert res.status_code == expected_status
                for k, v in expected_body.items():
                    assert res_dict[k] == v


def test_rest_state_change_prevented(app, record, users, json_patch_headers, json_headers, test_blueprint):
    url = url_for('invenio_records_rest.recid_item',
                  pid_value=recid_fetcher_v2(record.id, record).pid_value).replace('/api', '')
    print(url, app)
    print(url, app)
    orig_state = record['state']

    with app.test_client() as client:
        client.get(url_for('_tests.test_login_{}'.format(users['admin'].id)))
        res = client.get(
            url, headers=json_headers
        )
        res = client.patch(
            url,
            data=json.dumps([{"op": "replace", "path": "/state", "value": "boo"}]),
            headers=json_patch_headers)

        assert res.status_code == 403
        rec = ExampleRecord.get_record(record.id)
        assert rec['state'] == record['state']
