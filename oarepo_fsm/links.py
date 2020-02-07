#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions"""

from flask import url_for
from invenio_records_rest.links import default_links_factory

from oarepo_fsm.proxies import current_oarepo_fsm


def fsm_links_factory(pid, record=None, **kwargs):
    resp = default_links_factory(pid, record, **kwargs)
    if not record:
        return resp

    prefix = current_oarepo_fsm.get_record_fsm_prefix(record)
    if not prefix:
        return resp

    resp['state'] = url_for('oarepo_fsm.{0}_state'.format(prefix),
                            pid_value=pid.pid_value, _external=True)

    return resp
