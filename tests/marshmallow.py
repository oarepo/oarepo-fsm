# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# examples is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions"""
from invenio_records_rest.schemas import StrictKeysMixin
from invenio_records_rest.schemas.fields import SanitizedUnicode


class StatefulRecordSchemaV1(StrictKeysMixin):
    """Taxonomy schema."""
    b = SanitizedUnicode(required=False)


__all__ = ('StatefulRecordSchemaV1',)
