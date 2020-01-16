# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions"""

OAREPO_FSM = []
"""Record's FSM model configurations.
    OAREPO_FSM = [{
        # adds /fsm automatically to the item route
        item_route: '/records/<pid(recid):pid_value>',
        fsm: RecordModelFSM,
        # record $schema
        schema: '',
        # invenio permission factory
        transition_permission_factory: ''
    }]
"""
