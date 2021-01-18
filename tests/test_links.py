# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Test fsm links factory."""
import json

import pytest
from flask import url_for
from invenio_pidstore.fetchers import recid_fetcher_v2


def test_links_factory(app, record, json_headers):
    pid = recid_fetcher_v2(record.id, record).pid_value
    url = url_for('invenio_records_rest.recid_item',
                  pid_value=pid).replace('/api', '')

    with app.test_client() as client:
        res = client.get(url, headers=json_headers)
        assert res.status_code == 200
        res_dict = json.loads(res.data.decode('utf-8'))
        assert set(res_dict['links'].keys()) == {'self', 'transitions'}
        assert set(res_dict['links']['transitions'].keys()) == {'open', 'delete'}
