#
# Copyright (C) 2020 CESNET.
#
# examples is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions"""
import uuid

from invenio_db import db
from sqlalchemy_fsm import FSMField
from sqlalchemy_utils import UUIDType


class FSMRecord(db.Model):
    """Data model for FSM enabled record."""
    record_uuid = db.Column(
        UUIDType,
        primary_key=True,
        default=uuid.uuid4,
    )
    state = db.Column(FSMField, nullable=False)
