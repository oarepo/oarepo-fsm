# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# examples is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions"""
from __future__ import absolute_import, print_function

from flask.views import MethodView
from invenio_records_rest.views import need_record_permission, pass_record


class FSMRecordAction(MethodView):
    view_name = 'fsm_{0}'

    def __init__(self,
                 fsm_record_class=None,
                 fsm_record_schema=None,
                 transition_permission_factory=None,
                 fsm_endpoint_name=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.fsm_record_class = fsm_record_class
        self.fsm_record_schema = fsm_record_schema
        self.transition_permission_factory = transition_permission_factory
        self.fsm_endpoint_name = fsm_endpoint_name

    @pass_record
    def get(self, pid, record, **kwargs):
        """Get Record FSM data."""
        pass

    @pass_record
    @need_record_permission('transition_permission_factory')
    def post(self, pid, record, **kwargs):
        """Change Record state using FSM transition."""
        # current_search_client.indices.refresh()
        # current_search_client.indices.flush()
        # endpoint = 'invenio_records_rest.{0}_item'.format(self.published_endpoint_name)
        # return redirect(url_for(endpoint, pid_value=pid.pid_value, _external=True), code=302)
