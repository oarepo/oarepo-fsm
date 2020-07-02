# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions"""
from __future__ import absolute_import, print_function

from flask import jsonify, url_for, current_app
from invenio_records_rest import current_records_rest
from invenio_records_rest.views import pass_record
from invenio_rest import ContentNegotiatedMethodView

from oarepo_fsm.errors import RecordNotStatefulError
from oarepo_fsm.mixins import StatefulRecordMixin


def build_url_action_for_pid(pid, action):
    """Build urls for Loan actions."""
    return url_for(
        "oarepo_fsm.{0}_actions".format(pid.pid_type),
        pid_value=pid.pid_value,
        action=action,
        _external=True,
    )


def record_class_from_pid_type(pid_type):
    """Returns a Record class from a given pid_type."""
    try:
        prefix = current_records_rest.default_endpoint_prefixes[pid_type]
        return current_app.config.get('RECORDS_REST_ENDPOINTS', {})[prefix]['record_class']
    except KeyError:
        return None


class StatefulRecordActions(ContentNegotiatedMethodView):
    """StatefulRecord actions view."""
    view_name = '{0}_{1}'

    def __init__(self, serializers, ctx, *args, **kwargs):
        """Constructor."""
        super().__init__(serializers, *args, **kwargs)
        for key, value in ctx.items():
            setattr(self, key, value)

    @pass_record
    def get(self, pid, record, **kwargs):
        """Get Record FSM state response."""
        record_cls = record_class_from_pid_type(pid.pid_type)
        if not issubclass(record_cls, StatefulRecordMixin):
            raise RecordNotStatefulError(record_cls)

        actions = {}
        for act, _ in record_cls.user_transitions():
            actions[act] = build_url_action_for_pid(pid, act)

        result = dict(
            metadata=dict(
                state=record['state'],
            ),
            links=dict(
                actions=actions
            )
        )

        return jsonify(result)

    @pass_record
    def post(self, pid, record, **kwargs):
        """Change Record state using FSM transition."""
        # current_search_client.indices.refresh()
        # current_search_client.indices.flush()
        # endpoint = 'invenio_records_rest.{0}_item'.format(self.published_endpoint_name)
        # return redirect(url_for(endpoint, pid_value=pid.pid_value, _external=True), code=302)
