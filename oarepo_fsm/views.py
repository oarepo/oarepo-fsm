# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions."""
from __future__ import absolute_import, print_function

from functools import wraps

from flask import current_app, jsonify, url_for
from invenio_db import db
from invenio_records_rest import current_records_rest
from invenio_records_rest.views import pass_record
from invenio_rest import ContentNegotiatedMethodView

from oarepo_fsm.errors import ActionNotAvailableError, RecordNotStatefulError
from oarepo_fsm.mixins import FSMMixin


def validate_record_class(f):
    """
    Checks if record inherits from the FSMMixin.

    Checks if record inherits from the FSMMixin and
    adds a current record instance class to the wrapped function.
    """

    @wraps(f)
    def inner(self, pid, record, *args, **kwargs):
        record_cls = record_class_from_pid_type(pid.pid_type)
        if not issubclass(record_cls, FSMMixin):
            raise RecordNotStatefulError(record_cls)
        return f(self, pid=pid, record=record, record_cls=record_cls, *args, **kwargs)
    return inner


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


class FSMRecordActions(ContentNegotiatedMethodView):
    """StatefulRecord actions view."""

    view_name = '{0}_{1}'

    def __init__(self, serializers, ctx, *args, **kwargs):
        """Constructor."""
        super().__init__(serializers, *args, **kwargs)
        for key, value in ctx.items():
            setattr(self, key, value)

    @pass_record
    @validate_record_class
    def get(self, pid, record, record_cls, **kwargs):
        """Get Record FSM state response."""
        actions = {}
        for act in record_cls.user_actions().keys():
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
    @validate_record_class
    def post(self, pid, record, record_cls, action, **kwargs):
        """Change Record state using FSM action."""
        record = record_cls.get_record(record.id)
        ua = record.user_actions().get(action, None)
        if not ua:
            raise ActionNotAvailableError(action)

        # Invoke requested action for the current record
        ua(record)
        record.commit()
        db.session.commit()
        return self.make_response(
            pid,
            record,
            202
        )
