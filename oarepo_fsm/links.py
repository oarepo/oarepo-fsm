#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions."""

from flask import url_for
from invenio_records_rest.links import default_links_factory

from oarepo_fsm.mixins import FSMMixin
from oarepo_fsm.views import record_class_from_pid_type


def record_fsm_links_factory(pid, record=None, **kwargs):
    """Factory for record FSM links generation.

    :param pid: A Persistent Identifier instance.
    :param record: An instance of a Record.
    :returns: Dictionary containing a list of useful links + FSM link for the record.
    """
    links = default_links_factory(pid, record, **kwargs)
    rec_cls = record_class_from_pid_type(pid.pid_type)

    if issubclass(rec_cls, FSMMixin):
        fsm_url = url_for('oarepo_fsm.recid_fsm', pid_value=pid.pid_value, _external=True)
        links['fsm'] = fsm_url

    return links
