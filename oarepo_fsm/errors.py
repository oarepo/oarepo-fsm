#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions"""
import json

from invenio_rest.errors import RESTException


class FSMException(RESTException):
    """Base Exception for OArepo FSM module, inherit, don't raise."""
    code = 400

    @property
    def name(self):
        """The status name."""
        return type(self).__name__

    def get_body(self, environ=None):
        """Get the request body."""
        body = dict(
            status=self.code,
            message=self.get_description(environ),
            error_module="OArepo-FSM",
            error_class=self.name,
        )

        errors = self.get_errors()
        if self.errors:
            body["errors"] = errors

        if self.code and (self.code >= 500) and hasattr(g, "sentry_event_id"):
            body["error_id"] = str(g.sentry_event_id)

        return json.dumps(body)


class InvalidPermissionError(FSMException):
    """Raised when permissions are not satisfied for transition."""

    code = 403

    def __init__(self, permission=None, **kwargs):
        """Initialize exception."""
        self.description = (
            "This action is not permitted "
            "for your role '{}'".format(permission)
        )
        super().__init__(**kwargs)
