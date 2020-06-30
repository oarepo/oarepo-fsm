# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Test StatefulRecord REST API."""


def test_record_rest(app, json_headers, loan_created):
    """Test API GET call to fetch a loan by PID."""
    record_pid = loan_pid_fetcher(loan_created.id, loan_created)
    expected_links = {
        'actions': {
            'request': build_url_action_for_pid(loan_pid, 'request'),
            'checkout': build_url_action_for_pid(loan_pid, 'checkout')
        }
    }

    with app.test_client() as client:
        url = url_for('invenio_records_rest.loanid_item',
                      pid_value=loan_pid.pid_value)
        res = client.get(url, headers=json_headers)

    assert res.status_code == 200
    loan_dict = json.loads(res.data.decode('utf-8'))
    assert loan_dict['metadata']['state'] == loan_created['state']
    assert loan_dict['links'] == expected_links
