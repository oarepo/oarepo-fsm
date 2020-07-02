# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Test StatefulRecord REST API."""
import json

from flask import url_for
from flask_security import login_user
from invenio_pidstore.fetchers import recid_fetcher_v2

from oarepo_fsm.views import build_url_action_for_pid


def test_record_rest_endpoints(app, json_headers):
    """Test REST API FSM endpoints."""
    url_rules = [r.rule for r in app.url_map.iter_rules()]
    url_endpoints = [r.endpoint for r in app.url_map.iter_rules()]
    assert '/records/<pid(recid):pid_value>/fsm' in url_rules
    assert '/records/<pid(recid):pid_value>/fsm/<any(archive,close,open,publish):action>' in url_rules
    assert 'oarepo_fsm.recid_fsm' in url_endpoints
    assert 'oarepo_fsm.recid_actions' in url_endpoints


def test_fsm_rest(app, json_headers, record, users, test_blueprint):
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

        test_blueprint.add_url_rule('_login_{}'.format(user.id), view_func=_test_login_factory(user))
        app.register_blueprint(test_blueprint)
        with app.test_client() as client:
            client.get(url_for('_tests.test_login_{}'.format(user.id)))
            res = client.get(url, headers=json_headers)

        assert res.status_code == 200
        res_dict = json.loads(res.data.decode('utf-8'))
        assert res_dict['metadata']['state'] == record['state']
        assert res_dict['links'] == expected_links


def _test_login_factory(user):
    def test_login():
        login_user(user, remember=True)
        return 'OK'
    test_login.__name__ = '{}_{}'.format(test_login.__name__, user.id)
    return test_login
