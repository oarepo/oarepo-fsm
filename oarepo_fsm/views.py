# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions."""
from __future__ import absolute_import, print_function

from functools import wraps

from flask import current_app, jsonify, request, url_for, Response
from invenio_base.utils import obj_or_import_string
from invenio_db import db
from invenio_records_rest import current_records_rest
from invenio_records_rest.views import pass_record
from invenio_rest import ContentNegotiatedMethodView

from oarepo_fsm.errors import TransitionNotAvailableError, RecordNotStatefulError
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


def build_url_transition_for_pid(pid, transition):
    """Build urls for Loan transitions."""
    return url_for(
        "oarepo_fsm.{0}_transitions".format(pid.pid_type),
        pid_value=pid.pid_value,
        transition=transition,
        _external=True,
    )


def record_class_from_pid_type(pid_type):
    """Returns a Record class from a given pid_type."""
    try:
        prefix = current_records_rest.default_endpoint_prefixes[pid_type]
        return obj_or_import_string(
            current_app.config.get('RECORDS_REST_ENDPOINTS', {})[prefix]['record_class']
        )
    except KeyError:
        return None


class FSMRecordTransitions(ContentNegotiatedMethodView):
    """StatefulRecord transitions view."""

    view_name = '{0}_{1}'

    def __init__(self, serializers, ctx, indexer_class, *args, **kwargs):
        """Constructor."""
        super().__init__(serializers, *args, **kwargs)
        self.indexer_class = indexer_class
        for key, value in ctx.items():
            setattr(self, key, value)

    @pass_record
    @validate_record_class
    def post(self, pid, record, record_cls, transition, **kwargs):
        """Change Record state using FSM transition."""
        record = record_cls.get_record(record.id)
        ua = record.all_transitions().get(transition, None)
        if not ua:
            raise TransitionNotAvailableError(transition)

        # Invoke requested transition for the current record
        res = ua.function(record, **(request.json or {}))

        if ua.commit_record:
            record.commit()
            db.session.commit()

            if self.indexer_class().record_to_index(record)[0]:
                self.indexer_class().index(record)

        if res:
            if isinstance(res, Response):
                return res
            elif isinstance(res, dict):
                return jsonify(res)

        return self.make_response(
            pid,
            record,
            202
        )
