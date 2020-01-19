# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# examples is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions"""

OAREPO_FSM_ENABLED_RECORDS_REST_ENDPOINTS = {}
"""Record FSM endpoints configurations.
    OAREPO_FSM_ENABLED_RECORDS_REST_ENDPOINTS = {
        'records': {
            'json_schemas': [
                'records/stateful-stateful-record-v1.0.0.json'
            ],
            'record_marshmallow': RecordSchemaV1,
            'metadata_marshmallow': MetadataSchemaV1,

            'record_class': Record,
            'record_pid_type': 'recid',
            'fsm_record_class': FSMRecord,

            'transition_permission_factory': allow_authenticated,
            'fsm_permission_factory': allow_authenticated,
        }
    }
"""
