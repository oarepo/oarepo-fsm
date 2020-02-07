# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions"""
from __future__ import absolute_import, print_function

from flask import jsonify
from flask.views import MethodView
from invenio_records_rest.views import need_record_permission, pass_record
from sqlalchemy.inspection import inspect
from sqlalchemy_fsm import FSMField
from sqlalchemy_fsm.transition import InstanceBoundFsmTransition, ClassBoundFsmTransition

from oarepo_fsm.proxies import current_oarepo_fsm


class FSMRecordAction(MethodView):
    view_name = '{0}_state'

    def __init__(self,
                 fsm_record_schema=None,
                 fsm_pid_type=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.fsm_pid_type = fsm_pid_type
        self.fsm_record_schema = fsm_record_schema

    @pass_record
    def get(self, pid, record, **kwargs):
        """Get Record FSM data."""
        recfsm = current_oarepo_fsm.get_fsm_record(record)
        if not recfsm:
            response = jsonify({})
            response.status_code = 404
            return response

        result = {
            'transitions': []
        }

        for col in inspect(recfsm.__class__).columns:
            if isinstance(col.type, FSMField):
                result['state'] = getattr(recfsm, col.name)
                break

        for prop in dir(recfsm.__class__):
            fsm_field = getattr(recfsm.__class__, prop)
            if isinstance(fsm_field, ClassBoundFsmTransition):
                if recfsm.close.can_proceed():
                    result['transitions'].append(fsm_field)

            # if issubclass(fsm_field, FSMRecordModel):
            #         for meth in dir(fsm_field):
            #             if meth.startswith('_'):
            #                 continue
            #
            #             method = getattr(fsm_field, meth)
            #             if isinstance(method, InstanceBoundFsmTransition):
            #                 if method.can_proceed():
            #                     result['transitions'].append(meth)

        return jsonify(result)

    @pass_record
    @need_record_permission('transition_permission_factory')
    def post(self, pid, record, **kwargs):
        """Change Record state using FSM transition."""
        # current_search_client.indices.refresh()
        # current_search_client.indices.flush()
        # endpoint = 'invenio_records_rest.{0}_item'.format(self.published_endpoint_name)
        # return redirect(url_for(endpoint, pid_value=pid.pid_value, _external=True), code=302)
