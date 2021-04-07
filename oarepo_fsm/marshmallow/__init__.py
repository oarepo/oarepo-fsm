# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CESNET.
#
# OARepo-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""OArepo module that adds support for communities."""
from invenio_records_rest.schemas.fields import SanitizedUnicode
from marshmallow import Schema


class FSMRecordSchemaMixin(Schema):
    """FSMRecord schema mixin.

    Note: if you use your own state field, do not inherit from this mixin,
    write your own !
    """

    state = SanitizedUnicode(required=False)
